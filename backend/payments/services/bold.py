import hashlib
import hmac

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _get_secret():
    secret = settings.BOLD_INTEGRITY_SECRET
    if not secret:
        raise ImproperlyConfigured('BOLD_INTEGRITY_SECRET is required.')
    return secret


def calculate_integrity_hash(order_reference, amount_cents, currency):
    secret = _get_secret()
    payload = f'{order_reference}{amount_cents}{currency}{secret}'
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def validate_signature(payload_bytes, signature):
    secret = _get_secret()
    expected = hashlib.sha256(payload_bytes + secret.encode('utf-8')).hexdigest()
    return hmac.compare_digest(expected, signature or '')
