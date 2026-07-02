import base64
import binascii
from uuid import uuid4

from django.core.files.base import ContentFile
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from apps.models.image.models import Image
from utils.api.pagination import CustomPagination  # noqa: F401

from .validation import get_default_pipeline


class ImageSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField(read_only=True)

    class TagOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        parent = serializers.UUIDField(allow_null=True)

    @swagger_serializer_method(serializer_or_field=TagOutputSerializer(many=True))
    def get_tags(self, obj):
        return [
            {
                "id": image_tag.tag_id,
                "name": image_tag.tag.name,
                "parent": image_tag.tag.parent_id,
            }
            for image_tag in obj.image_tags.all()
            if image_tag.tag
        ]

    class Meta:
        model = Image
        fields = (
            "id",
            "user",
            "created",
            "modified",
            "file",
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
            "validation_model_type",
            "image_score",
            "image_min_score",
            "image_label_target",
            "tags",
            "is_reward_claimed",
            "reward_withdrawal",
            "reward_rule",
            "reward_amount",
            "reward_claimed_at",
        )
        read_only_fields = (
            "user",
            "file_name",
            "file_extension",
            "uploaded_at",
            "is_reward_claimed",
            "reward_withdrawal",
            "reward_rule",
            "reward_amount",
            "reward_claimed_at",
        )

    def validate_file(self, value):
        """Resize to JPEG ≤1500px."""
        return get_default_pipeline().process(value)


class ImageBase64UploadSerializer(serializers.ModelSerializer):
    image_base64 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "image_base64",
            "captured_at",
            "ip_address",
            "device_type",
            "device_brand",
            "device_model",
            "operating_system",
            "browser_name",
            "browser_version",
            "camera_brand",
            "camera_model",
            "validation_model_type",
            "image_score",
            "image_min_score",
            "image_label_target",
        )

    def _decode_base64_image(self, value):
        raw_data = value
        extension = "jpg"

        if ";base64," in value:
            header, raw_data = value.split(";base64,", 1)
            if header.startswith("data:image/"):
                extension = header.split("data:image/")[1].lower()

        ext_map = {
            "jpeg": "jpg",
            "jpg": "jpg",
            "png": "png",
            "webp": "webp",
            "gif": "gif",
        }
        extension = ext_map.get(extension, "jpg")

        try:
            decoded = base64.b64decode(raw_data)
        except (ValueError, binascii.Error) as exc:
            raise serializers.ValidationError("image_base64 no es valido.") from exc

        if not decoded:
            raise serializers.ValidationError("image_base64 no contiene datos.")

        filename = f"image_{uuid4().hex}.{extension}"
        return ContentFile(decoded, name=filename)

    def create(self, validated_data):
        image_base64 = validated_data.pop("image_base64")
        raw_file = self._decode_base64_image(image_base64)
        validated_data["file"] = get_default_pipeline().process(raw_file)
        return super().create(validated_data)
