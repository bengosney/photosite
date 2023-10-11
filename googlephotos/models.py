# Standard Library
from typing import Self

# Django
from django.db import models

# Third Party
from google.auth.external_account_authorized_user import Credentials


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
    uid = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    product_url = models.CharField(max_length=255)
    cover_photo_base_url = models.CharField(max_length=255)
    cover_photo_media_item_id = models.CharField(max_length=255)
    media_items_count = models.IntegerField()


class Photo(models.Model):
    uid = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255)
    product_url = models.CharField(max_length=255)
    media_metadata = models.CharField(max_length=255)
