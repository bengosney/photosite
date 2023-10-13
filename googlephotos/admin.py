# Django
from django.contrib import admin

# Locals
from .models import Album, Photo


class PhotoAdmin(admin.ModelAdmin):
    pass


class AlbumAdmin(admin.ModelAdmin):
    pass


admin.site.register(Photo, PhotoAdmin)
admin.site.register(Album, AlbumAdmin)
