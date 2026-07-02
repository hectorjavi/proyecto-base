from django.contrib import admin

from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "created", "modified")
    search_fields = ("name",)
    list_filter = ("parent",)
    ordering = ("name",)
