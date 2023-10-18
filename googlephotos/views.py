# Standard Library
from datetime import datetime
from typing import Any

# Django
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

# Locals
from .google import GoogleAlbum as GoogleAlbum
from .google import GooglePhoto as GooglePhoto
from .google import GooglePhotosApi
from .models import Album, Photo, Token


class AlbumView(TemplateView):
    template_name = "googlephotos/album.html"

    def update_photos(self, album: Album):
        i = 0
        for photo in GooglePhoto.from_album(album.uid):
            _, created = Photo.from_google_photo(photo, album)
            i += int(created)
            if i > 5:
                break

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        album = Album.objects.get(uid=kwargs["uid"])

        self.update_photos(album)

        context["album"] = album
        context["photos"] = Photo.objects.filter(album=album)
        context["album_url"] = self.request.path

        return context


class AlbumListView(TemplateView):
    template_name = "googlephotos/albums.html"

    def update_albums(self):
        for google_album in GoogleAlbum.all():
            album, _ = Album.objects.update_or_create(
                uid=google_album.id,
                defaults={
                    "cover_photo_base_url": google_album.coverPhotoBaseUrl,
                    "cover_photo_media_item_id": google_album.coverPhotoMediaItemId,
                    "media_items_count": google_album.mediaItemsCount,
                    "product_url": google_album.productUrl,
                    "title": google_album.title,
                },
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["albums"] = Album.objects.all()
        context["albums_url"] = self.request.path

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

        # return super().get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("googlephotos:albums"))


class AuthView(RedirectView):
    template_name = "googlephotos/auth.html"

    def get_redirect_url(self, *args, **kwargs):
        api = GooglePhotosApi()

        path = reverse("googlephotos:callback")
        redirect_uri = self.request.build_absolute_uri(path)
        url, state = api.get_auth_url(redirect_uri)
        self.request.session["google_auth_state"] = state

        return url
