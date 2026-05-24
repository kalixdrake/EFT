from dataclasses import dataclass
from decimal import Decimal

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
    raw: dict


@dataclass(frozen=True)
class SkydropxShipmentResult:
    shipment_id: str
    tracking_number: str
    label_url: str
    status: str


class SkydropxClient:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or settings.SKYDROPX_API_KEY
        self.base_url = (base_url or settings.SKYDROPX_API_BASE_URL).rstrip('/')
        if not self.api_key:
            raise ImproperlyConfigured('SKYDROPX_API_KEY is required.')

    def _headers(self):
        return {
            'Authorization': f'Token token={self.api_key}',
            'Content-Type': 'application/json',
        }

    def get_quotes(self, zip_from, zip_to, parcel, carriers=None):
        payload = {
            'zip_from': zip_from,
            'zip_to': zip_to,
            'parcel': parcel,
        }
        if carriers:
            payload['carriers'] = [{'name': name} for name in carriers]
        response = requests.post(
            f'{self.base_url}/quotations',
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(response.text)
        data = response.json()
        quotes = []
        for item in data:
            quotes.append(
                SkydropxQuote(
                    carrier=item.get('provider', ''),
                    service=item.get('service_level_name', ''),
                    service_code=item.get('service_level_code', ''),
                    estimated_days=int(item.get('days') or 0),
                    cost=Decimal(str(item.get('total_pricing') or item.get('amount_local') or '0')),
                    currency=item.get('currency_local') or 'COP',
                    raw=item,
                )
            )
        return quotes

    def create_shipment(self, address_from, address_to, parcel, carrier, service_code, order_reference):
        payload = {
            'address_from': address_from,
            'address_to': address_to,
            'parcel': parcel,
            'carrier': carrier,
            'service_code': service_code,
            'order': order_reference,
        }
        response = requests.post(
            f'{self.base_url}/shipments',
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(response.text)
        data = response.json()
        attributes = data.get('data', {}).get('attributes', {}) if isinstance(data, dict) else {}
        return SkydropxShipmentResult(
            shipment_id=str(data.get('data', {}).get('id', '')),
            tracking_number=str(attributes.get('tracking_number', '')),
            label_url=str(attributes.get('label_url', '')),
            status=str(attributes.get('status', '')),
        )

    def get_tracking(self, shipment_id):
        response = requests.get(
            f'{self.base_url}/shipments/{shipment_id}',
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise SkydropxError(response.text)
        return response.json()
