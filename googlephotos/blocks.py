# Wagtail
from wagtail import blocks


class AlbumBlock(blocks.ChooserBlock):
    target_model = "googlephotos.Album"
    # widget = "album"

    # class Meta:
    #    template = "googlephotos/blocks/album.html"
    #    icon = "image"
