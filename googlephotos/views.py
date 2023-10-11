# Standard Library
from datetime import datetime
from typing import Any

# Django
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

# Locals
from .google import Album, GooglePhotosApi
from .models import Token


class AlbumsView(TemplateView):
    template_name = "googlephotos/albums.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["albums"] = Album.all()

        return context


class CallbackView(TemplateView):
    template_name = "googlephotos/callback.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        api = GooglePhotosApi()

        token_args = {}
        for key in ["code", "scope"]:
            if key in request.GET:
                token_args[key] = request.GET.get(key)

        token_data = api.fetch_token(**token_args)
        token = Token()
        token.access_token = token_data["access_token"]
        token.expires_at = datetime.fromtimestamp(token_data["expires_at"])
        token.expires_in = token_data["expires_in"]
        token.scope = token_data["scope"]
        token.token_type = token_data["token_type"]
        token.save()

        return super().get(request, *args, **kwargs)


class AuthView(RedirectView):
    template_name = "googlephotos/auth.html"

    def get_redirect_url(self, *args, **kwargs):
        api = GooglePhotosApi()

        path = reverse("googlephotos:callback")
        redirect_uri = self.request.build_absolute_uri(path)
        url, state = api.get_auth_url(redirect_uri)
        self.request.session["google_auth_state"] = state

        return url
