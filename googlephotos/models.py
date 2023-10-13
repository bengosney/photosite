# Standard Library
from typing import Self

# Django
from django.db import models
from django.urls import reverse_lazy

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


class Photo(models.Model):
    uid = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255)
    product_url = models.CharField(max_length=255)
    media_metadata = models.CharField(max_length=255)
    album = models.ForeignKey(Album, on_delete=models.PROTECT, null=True)
    image = models.ImageField(upload_to="googlephotos", null=True)

    def __str__(self) -> str:
        return f"{self.filename}"

    @property
    def url(self):
        return self.base_url

    @classmethod
    def from_google_photo(cls, google_photo: GooglePhoto, album: Album | GoogleAlbum) -> Self:
        photo, created = cls.objects.update_or_create(
            uid=google_photo.id,
            defaults={
                "base_url": google_photo.baseUrl,
                "filename": google_photo.filename,
                "mime_type": google_photo.mimeType,
                "product_url": google_photo.productUrl,
                "media_metadata": google_photo.mediaMetadata,
                "album": album,
            },
        )

        if created or photo.image.name == "":
            file = google_photo.get_file(2048, 1024)
            if file is not None:
                photo.image.save(photo.filename, file)

        return photo
