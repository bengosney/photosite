# Wagtail
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

# Locals
from .models import Album


class AlbumAdmin(SnippetViewSet):
    model = Album
    menu_label = "Albums"
    menu_icon = "image"
    list_display = ("title", "media_items_count")
    list_filter = ("title", "media_items_count")
    inspect_view_enabled = True


register_snippet(AlbumAdmin)
