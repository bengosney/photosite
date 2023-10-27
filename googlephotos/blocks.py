# Wagtail
from wagtail.blocks import ChooserBlock, StructBlock, StructValue

# Locals
from .models import AlbumPage


class AlbumListStructValue(StructValue):
    def albums(self):
        return AlbumPage.objects.all()  # descendant_of(self)


class AlbumBlock(ChooserBlock):
    target_model = "googlephotos.Album"
    # widget = "album"

    class Meta:
        template = "googlephotos/blocks/album.html"
        icon = "image"


class AlbumListBlock(StructBlock):
    class Meta:
        template = "googlephotos/blocks/album-list.html"
        icon = "image"
        value_class = AlbumListStructValue
