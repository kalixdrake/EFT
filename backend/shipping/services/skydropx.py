import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SkydropxError(RuntimeError):
    pass


@dataclass(frozen=True)
class SkydropxQuote:
    carrier: str
    service: str
    service_code: str
    estimated_days: int
    cost: Decimal
    currency: str
    quotation_id: str  # ID de la cotización completa (para crear envío)
    rate_id: str       # ID de esta tarifa específica (para crear envío)
    raw: dict


@dataclass(frozen=True)
class SkydropxShipmentResult:
    shipment_id: str
    tracking_number: str
    label_url: str
    status: str


class SkydropxClient:
    """
    Cliente para la API de Skydropx (sb-pro / pro).
    Usa OAuth2 client_credentials para obtener Bearer tokens.

    Credenciales en settings:
      - SKYDROPX_CLIENT_ID     → API_KEY_SKYDROPX[_SANDBOX]
      - SKYDROPX_CLIENT_SECRET → API_SECRET_KEY_SKYDROPX[_SANDBOX]
    """

    _token_cache: dict = {}  # cache de clase: {client_id: {token, expires_at}}

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, base_url: Optional[str] = None):
        self.client_id = client_id or settings.SKYDROPX_CLIENT_ID
        self.client_secret = client_secret or settings.SKYDROPX_CLIENT_SECRET
        self.base_url = (base_url or settings.SKYDROPX_API_BASE_URL).rstrip('/')
        if not self.client_id or not self.client_secret:
            raise ImproperlyConfigured('SKYDROPX_CLIENT_ID y SKYDROPX_CLIENT_SECRET son requeridos.')

    def _get_access_token(self) -> str:
        cache = SkydropxClient._token_cache
        entry = cache.get(self.client_id)
        if entry and time.time() < entry['expires_at'] - 60:
            return entry['token']

        response = requests.post(
            f'{self.base_url}/oauth/token',
            json={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
            },
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(f'OAuth token error: {response.text}')
        data = response.json()
        token = data['access_token']
        expires_in = data.get('expires_in', 7200)
        cache[self.client_id] = {'token': token, 'expires_at': time.time() + expires_in}
        return token

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json',
        }

    def get_quotes(self, address_from: dict, address_to: dict, parcel: dict, carriers: Optional[list] = None, declared_amount: Optional[float] = None) -> list:
        """
        Cotiza envíos.

        address_from / address_to deben incluir:
          country_code, postal_code, area_level1, area_level2

        parcel debe incluir: weight, length, width, height (numéricos)
        declared_amount: valor declarado (requerido para CO; va dentro de cada parcel)
        """
        parcels = [{
            'weight': float(parcel['weight']),
            'length': int(float(parcel['length'])),
            'width': int(float(parcel['width'])),
            'height': int(float(parcel['height'])),
            'declared_amount': declared_amount or 10000,
        }]

        quotation_payload: dict = {
            'address_from': {
                'country_code': address_from['country_code'],
                'postal_code': address_from['postal_code'],
                'area_level1': address_from['area_level1'],
                'area_level2': address_from['area_level2'],
            },
            'address_to': {
                'country_code': address_to['country_code'],
                'postal_code': address_to['postal_code'],
                'area_level1': address_to['area_level1'],
                'area_level2': address_to['area_level2'],
            },
            'parcels': parcels,
        }
        if carriers:
            quotation_payload['requested_carriers'] = carriers

        response = requests.post(
            f'{self.base_url}/quotations',
            json={'quotation': quotation_payload},
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(response.text)

        data = response.json()
        quotation_id = data.get('id', '')

        # Poll until is_completed (async processing, usually < 5s)
        if not data.get('is_completed') and quotation_id:
            data = self._poll_quotation(quotation_id, max_wait=20)

        rates = data.get('rates', [])
        _valid_statuses = frozenset({
            'approved', 'coverage_checked', 'price_found_internal', 'price_found_external',
        })
        quotes = []
        for rate in rates:
            status_val = rate.get('status', '')
            if status_val not in _valid_statuses:
                continue
            total = rate.get('total') or rate.get('amount') or '0'
            if not total or float(total) <= 0:
                continue
            quotes.append(
                SkydropxQuote(
                    carrier=rate.get('provider_name', ''),
                    service=rate.get('provider_service_name', ''),
                    service_code=rate.get('provider_service_code', ''),
                    estimated_days=int(rate.get('days') or 0),
                    cost=Decimal(str(total)),
                    currency=rate.get('currency_code') or 'MXN',
                    quotation_id=quotation_id,
                    rate_id=rate.get('id', ''),
                    raw=rate,
                )
            )
        return quotes

    def _poll_quotation(self, quotation_id: str, max_wait: int = 20) -> dict:
        """Poll GET /quotations/{id} until is_completed or timeout."""
        deadline = time.time() + max_wait
        interval = 2
        while time.time() < deadline:
            time.sleep(interval)
            resp = requests.get(
                f'{self.base_url}/quotations/{quotation_id}',
                headers=self._headers(),
                timeout=15,
            )
            if resp.status_code >= 400:
                raise SkydropxError(resp.text)
            data = resp.json()
            if data.get('is_completed'):
                return data
        return data  # Return last response even if not completed

    def create_shipment(
        self,
        quotation_id: str,
        rate_id: str,
        address_from: dict,
        address_to: dict,
        packages: list | None = None,
    ) -> SkydropxShipmentResult:
        """
        Crea un envío usando la cotización y tarifa previamente obtenidas.

        address_from / address_to deben incluir campos completos:
          country_code, postal_code, area_level1, area_level2, area_level3,
          street1, name, phone, email, reference

        packages: lista de paquetes. Cada item puede incluir:
          package_number (str, 1-based), consignment_note, package_type.
          Si no se provee, se genera un paquete por defecto.
        """
        if not packages:
            # 53102400 = "Partes y accesorios para vehículos" — valid SAT code for sandbox domestic MX
            packages = [{'package_number': '1', 'consignment_note': '53102400', 'package_type': '4G'}]

        def _build_address(addr: dict) -> dict:
            reference = addr.get('reference') or addr.get('street1') or addr.get('name', 'Dirección')
            return {
                'country_code': addr['country_code'],
                'postal_code': addr['postal_code'],
                'area_level1': addr['area_level1'],
                'area_level2': addr['area_level2'],
                'area_level3': addr.get('area_level3', addr['area_level2']),
                'street1': addr.get('street1', ''),
                'name': addr.get('name', ''),
                'company': addr.get('company', ''),
                'phone': addr.get('phone', ''),
                'email': addr.get('email', ''),
                'reference': reference,
            }

        payload = {
            'shipment': {
                'quotation_id': quotation_id,
                'rate_id': rate_id,
                'address_from': _build_address(address_from),
                'address_to': _build_address(address_to),
                'packages': packages,
            }
        }
        response = requests.post(
            f'{self.base_url}/shipments/',
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(response.text)

        data = response.json()
        shipment_data = data.get('data', {})
        attributes = shipment_data.get('attributes', {})

        # tracking_number and label_url come in the included packages
        tracking_number = attributes.get('master_tracking_number', '')
        label_url = ''
        for included in data.get('included', []):
            if included.get('type') == 'package':
                pkg_attrs = included.get('attributes', {})
                tracking_number = tracking_number or pkg_attrs.get('tracking_number', '')
                label_url = label_url or pkg_attrs.get('label_url', '')
                if tracking_number and label_url:
                    break

        return SkydropxShipmentResult(
            shipment_id=str(shipment_data.get('id', '')),
            tracking_number=str(tracking_number),
            label_url=str(label_url),
            status=str(attributes.get('workflow_status', '')),
        )

    def get_tracking(self, shipment_id: str) -> dict:
        response = requests.get(
            f'{self.base_url}/shipments/{shipment_id}',
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(response.text)
        return response.json()
