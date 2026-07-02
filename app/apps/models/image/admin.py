from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile

from apps.models.image.api.validation import get_default_pipeline
from apps.models.image_tag.models import ImageTag

from . import models


class ImageAdminForm(forms.ModelForm):
    """Admin form that runs the same resize + JPEG conversion pipeline as the REST API."""

    class Meta:
        model = models.Image
        fields = "__all__"

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not isinstance(file, UploadedFile):
            return file
        try:
            return get_default_pipeline().process(file)
        except Exception as exc:
            raise forms.ValidationError(str(exc)) from exc


class ImageTagInline(admin.TabularInline):
    model = ImageTag
    extra = 1
    autocomplete_fields = ("tag",)


class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm
    list_display = (
        "id",
        "user",
        "validation_model_type",
        "image_score",
        "image_min_score",
        "image_label_target",
        "file_name",
        "file_extension",
        "captured_at",
        "uploaded_at",
        "ip_address",
        "device_type",
        "device_brand",
        "device_model",
        "operating_system",
        "browser_name",
        "browser_version",
        "camera_brand",
        "camera_model",
        "tags_display",
    )
    list_per_page = 15
    search_fields = ["file_name", "id"]
    ordering = ["-uploaded_at"]
    date_hierarchy = "uploaded_at"
    list_filter = ["device_type"]
    filter_horizontal = []
    inlines = [ImageTagInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("image_tags__tag")

    @admin.display(description="Tags")
    def tags_display(self, obj):
        tags = [image_tag.tag.name for image_tag in obj.image_tags.all() if image_tag.tag]
        return ", ".join(tags) if tags else "-"


admin.site.register(models.Image, ImageAdmin)
