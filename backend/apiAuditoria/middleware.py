from .services import persist_audit_event, should_audit


class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if should_audit(request, response):
            persist_audit_event(request, response)
        return response

