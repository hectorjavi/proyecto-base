from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel

from apps.models.image.models import Image
from apps.models.tag.models import Tag


class ImageTag(UUIDModel, TimeStampedModel):
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="image_tags",
        verbose_name="Imagen",
        help_text="Imagen asociada.",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="image_tags",
        verbose_name="Etiqueta",
        help_text="Etiqueta asociada.",
    )

    class Meta:
        db_table = "image_tags"
        verbose_name = "Relacion imagen-etiqueta"
        verbose_name_plural = "Relaciones imagen-etiqueta"
        indexes = [
            models.Index(fields=["image"]),
            models.Index(fields=["tag"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["image", "tag"],
                name="uq_image_tags_image_tag",
            )
        ]

    def __str__(self) -> str:
        return f"{self.image_id} -> {self.tag_id}"
