# Django
from django.shortcuts import redirect

# Locals
from .exceptions import RedirectException


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, RedirectException):
            return redirect(exception.url)
