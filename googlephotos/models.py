# Standard Library
import json
from collections.abc import Iterable
from typing import Any, Self

# Django
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone

# Wagtail
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.models import Page

# Third Party
from google.auth.external_account_authorized_user import Credentials

# Locals
from .google import GoogleAlbum, GooglePhoto


class Token(models.Model):
    access_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    expires_in = models.IntegerField()
    scope = (models.JSONField(),)
    token_type = models.CharField(max_length=10)

    @classmethod
    def most_recent(cls) -> Self:
        return cls.objects.latest("expires_at")

    def as_credentials(self):
        return Credentials(
            token=self.access_token,
            expiry=self.expires_at,
            scopes=self.scope,
        )


class Album(models.Model):
    uid = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    product_url = models.CharField(max_length=255)
    cover_photo_base_url = models.CharField(max_length=255)
    cover_photo_media_item_id = models.CharField(max_length=255)
    media_items_count = models.IntegerField()

    def __str__(self) -> str:
        return self.title

    @property
    def url(self):
        return reverse_lazy("googlephotos:album", kwargs={"uid": self.uid})

    @property
    def photos(self) -> Iterable["Photo"]:
        return Photo.objects.filter(album=self)


class Photo(models.Model):
    show = models.BooleanField(default=True)
    uid = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255)
    product_url = models.CharField(max_length=255)
    media_metadata = models.CharField(max_length=255)
    album = models.ForeignKey(Album, on_delete=models.PROTECT, null=True)
    photo = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    creation_time = models.DateTimeField()

    _metadata = None

    class Meta:
        ordering = ["-creation_time"]

    def __str__(self) -> str:
        return f"{self.filename}"

    @property
    def metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            self._metadata = json.loads(self.media_metadata)
        return self._metadata

    @property
    def url(self):
        return self.base_url

    @classmethod
    def from_google_photo(cls, google_photo: GooglePhoto, album: Album | GoogleAlbum) -> tuple[Self, bool]:
        metadata = json.loads(google_photo.mediaMetadata.replace("'", '"'))
        photo, created = cls.objects.update_or_create(
            uid=google_photo.id,
            defaults={
                "base_url": google_photo.baseUrl,
                "filename": google_photo.filename,
                "mime_type": google_photo.mimeType,
                "product_url": google_photo.productUrl,
                "media_metadata": google_photo.mediaMetadata,
                "album": album,
                "creationTime": metadata.get("creationTime", timezone.now()),
            },
        )

        if created or photo.photo is None:
            width = google_photo.mediaMetadata.get("width", 2048)
            height = google_photo.mediaMetadata.get("height", 1024)
            img_file = google_photo.get_file(width, height)
            img = Image(
                file=img_file,
                title=photo.filename,
                width=width,
                height=height,
            )
            img.save()
            photo.photo = img
            photo.save()
            created = True

        return photo, created


class AlbumPage(Page):
    intro = RichTextField(blank=True)
    album = models.ForeignKey(Album, on_delete=models.PROTECT, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("album"),
    ]
