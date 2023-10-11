class RedirectException(Exception):
    def __init__(self, url, *args: object) -> None:
        super().__init__(*args)
        self._url = url

    @property
    def url(self):
        return self._url
