# Standard Library
import json
import os
import pickle
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Self

# Third Party
import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from icecream import ic


class GooglePhotosApi:
    _instance = None

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

        self._credentials = None

    @property
    def credentials(self):
        # is checking if there is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, "rb") as token:
                self._credentials = pickle.load(token)

        # if there is no pickle file with stored credentials, create one using google_auth_oauthlib.flow
        if not self._credentials or not self._credentials.valid:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self._credentials = flow.run_local_server(port=8000)

            with open(self.cred_pickle_file, "wb") as token:
                pickle.dump(self._credentials, token)

        return self._credentials

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

        return response.json()


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
class Photo:
    baseUrl: str
    filename: str
    id: str
    mimeType: str
    productUrl: str
    mediaMetadata: Any

    @classmethod
    def from_album(cls, album: "str | Album") -> Iterable[Self]:
        album_id = album.id if isinstance(album, Album) else album
        return ApiResponse("mediaItems", "mediaItems:search", {"albumId": album_id}, cls)


@dataclass
class Album:
    coverPhotoBaseUrl: str
    coverPhotoMediaItemId: str
    id: str
    mediaItemsCount: int
    productUrl: str
    title: str

    @classmethod
    def all(cls) -> Iterable[Self]:
        return ApiResponse("albums", "albums", None, cls)

    def photos(self) -> Iterable[Photo]:
        return Photo.from_album(self)


for album in Album.all():
    ic(album.title)
