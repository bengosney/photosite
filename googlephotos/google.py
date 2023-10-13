# Standard Library
import json
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Self

# Django
from django.core import files
from django.urls import reverse_lazy

# Third Party
import requests
from google.auth.external_account_authorized_user import Credentials as eCreds
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as Creds
from google_auth_oauthlib.flow import Flow

# Locals
from .exceptions import RedirectException


class GooglePhotosApi:
    _instance = None
    _client = None
    _credentials = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.api_name = "website"
        self.client_secret_file = r"./credentials/client_secret.json"
        self.api_version = "v1"
        self.scopes = ["https://www.googleapis.com/auth/photoslibrary"]
        self.cred_pickle_file = f"./credentials/token_{self.api_name}_{self.api_version}.pickle"
        self.cred_json_file = f"./credentials/token_{self.api_name}_{self.api_version}.json"

    @property
    def client(self) -> Flow:
        if self._client is None:
            self._client = Flow.from_client_secrets_file(self.client_secret_file, self.scopes)
        return self._client

    def get_auth_url(self, redirect_uri: str):
        self.client.redirect_uri = redirect_uri
        return self.client.authorization_url()

    def fetch_token(self, **kwargs):
        token_data = self.client.fetch_token(**kwargs)
        self._credentials = self.client.credentials
        return token_data

    @property
    def credentials(self) -> Creds | eCreds:
        if not self._credentials or not self._credentials.valid:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())

        if self._credentials is None:
            raise RedirectException(reverse_lazy("googlephotos:auth"))

        return self._credentials

    def raw_request(self, url: str):
        headers = {"content-type": "application/json", "Authorization": f"Bearer {self.credentials.token}"}
        return requests.request("GET", url, headers=headers)

    def request(self, path: str, payload: dict | None = None, next: str | None = None):
        url = f"https://photoslibrary.googleapis.com/v1/{path}"

        headers = {"content-type": "application/json", "Authorization": f"Bearer {self.credentials.token}"}

        try:
            if payload is None:
                if next is not None:
                    url += f"?pageToken={next}"
                response = requests.request("GET", url, headers=headers)
            else:
                if next is not None:
                    payload["pageToken"] = next
                response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        except Exception as err:
            print("Request error", err)
            raise err

        data = response.json()

        try:
            if data["error"]["code"] == 401:
                raise RedirectException(reverse_lazy("googlephotos:auth"))
        except KeyError:
            pass

        return data


class ApiResponse:
    def __init__(self, key: str, path: str, payload: dict | None, dataclassType: Any) -> None:
        self._results = {key: [], "nextPageToken": None}
        self._position = -1
        self._key = key
        self._path = path
        self._payload = payload
        self._dataclassType = dataclassType

    def __iter__(self):
        return self

    def __next__(self):
        self._position += 1
        try:
            return self._get()
        except IndexError:
            try:
                api = GooglePhotosApi()
                self._results = api.request(self._path, self._payload, next=self._results["nextPageToken"])
                self._position = 0
                return self._get()
            except (KeyError, IndexError):
                raise StopIteration

    def _get(self):
        while True:
            try:
                return self._dataclassType(**self._results[self._key][self._position])
            except TypeError:
                self._position += 1


@dataclass
class GooglePhoto:
    baseUrl: str
    filename: str
    id: str
    mimeType: str
    productUrl: str
    mediaMetadata: Any

    @classmethod
    def from_album(cls, album: "str | GoogleAlbum") -> Iterable[Self]:
        album_id = album.id if isinstance(album, GoogleAlbum) else album
        return ApiResponse("mediaItems", "mediaItems:search", {"albumId": album_id}, cls)

    def get_file(self, width: int, height: int):
        api = GooglePhotosApi()
        response = api.raw_request(f"{self.baseUrl}=w{width}-h{height}")
        if response.status_code == requests.codes.ok:
            fp = BytesIO()
            fp.write(response.content)

            return files.File(fp)

        return None


@dataclass
class GoogleAlbum:
    id: str
    coverPhotoBaseUrl: str
    coverPhotoMediaItemId: str
    mediaItemsCount: int
    productUrl: str
    title: str

    @classmethod
    def all(cls) -> Iterable[Self]:
        return ApiResponse("albums", "albums", None, cls)

    def photos(self) -> Iterable[GooglePhoto]:
        return GooglePhoto.from_album(self)
