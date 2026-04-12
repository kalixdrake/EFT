from rest_framework.views import exception_handler


class ErrorEnvelope(dict):
    """
    Envelope compatible con tests legacy: expone code/message/details,
    pero mantiene acceso de primer nivel a los campos originales.
    """

    def __contains__(self, key):
        details = dict.get(self, "details", {})
        return key in details or super().__contains__(key)

    def __getitem__(self, key):
        details = dict.get(self, "details", {})
        if key in details:
            return details[key]
        return super().__getitem__(key)

    def get(self, key, default=None):
        details = dict.get(self, "details", {})
        if key in details:
            return details.get(key, default)
        return super().get(key, default)


def eft_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = response.data
    if isinstance(data, dict) and "code" in data and "message" in data:
        return response

    response.data = ErrorEnvelope(
        {
            "code": f"HTTP_{response.status_code}",
            "message": "Request failed",
            "details": data,
        }
    )
    return response
