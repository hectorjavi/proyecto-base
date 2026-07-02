from django.contrib import admin

from .models import ImageTag


@admin.register(ImageTag)
class ImageTagAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "tag", "created", "modified")
    search_fields = ("image__file_name", "tag__name")
    list_filter = ("tag",)
