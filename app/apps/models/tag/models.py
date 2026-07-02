from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel


class Tag(UUIDModel, TimeStampedModel):
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre de la etiqueta.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Etiqueta padre",
        help_text="Etiqueta padre para construir jerarquias.",
    )

    class Meta:
        db_table = "tags"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["parent"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                condition=models.Q(parent__isnull=False),
                name="uq_tags_parent_name_not_null",
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(parent__isnull=True),
                name="uq_tags_name_root",
            ),
        ]

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name
