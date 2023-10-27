# Wagtail
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField
from wagtail.models import Page

# First Party
from googlephotos.blocks import AlbumListBlock


class HomePage(Page):
    content = StreamField(
        [
            ("Paragraph", RichTextBlock()),
            ("AlbumList", AlbumListBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("content"),
    ]
