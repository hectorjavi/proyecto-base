# from django.db import models
from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel


class DeviceType(models.TextChoices):
    MOBILE = "mobile", "Mobile"
    DESKTOP = "desktop", "Desktop"
    TABLET = "tablet", "Tablet"
    UNKNOWN = "unknown", "Unknown"


# Create your models here.
class Image(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
        # editable=False,
        verbose_name="Usuario",
        help_text="Usuario propietario que creo este archivo.",
    )
    file = models.ImageField(
        upload_to="images/%Y/%m/%d/",
        verbose_name="Archivo",
        help_text="Imagen a almacenar en el sistema.",
    )
    file_name = models.CharField(
        max_length=255,
        editable=False,
        blank=True,
        verbose_name="Nombre del archivo",
        help_text="Nombre original del archivo, calculado automaticamente.",
    )
    file_extension = models.CharField(
        max_length=10,
        editable=False,
        blank=True,
        verbose_name="Extension",
        help_text="Extension del archivo (ejemplo: .jpg, .png), calculada automaticamente.",
    )
    captured_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de captura",
        help_text="Fecha y hora en que se capturo la imagen.",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de subida",
        help_text="Fecha y hora en que el archivo fue subido.",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Direccion IP",
        help_text="IP desde donde se envio la imagen.",
    )

    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.UNKNOWN,
        verbose_name="Tipo de dispositivo",
        help_text="Tipo de dispositivo que genero la imagen.",
    )
    device_brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Marca del dispositivo",
        help_text="Marca del dispositivo (ejemplo: Samsung, Apple).",
    )
    device_model = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Modelo del dispositivo",
        help_text="Modelo del dispositivo que capturo/subio la imagen.",
    )

    operating_system = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Sistema operativo",
        help_text="Sistema operativo del dispositivo.",
    )
    browser_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Navegador",
        help_text="Nombre del navegador desde donde se envio la imagen.",
    )
    browser_version = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Version del navegador",
        help_text="Version del navegador del cliente.",
    )

    camera_brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Marca de camara",
        help_text="Marca de la camara, si esta disponible.",
    )
    camera_model = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Modelo de camara",
        help_text="Modelo de la camara, si esta disponible.",
    )
    validation_model_type = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Modelo de validacion",
        help_text="Modelo(s) ML usados para validar la imagen.",
    )
    image_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Score de imagen",
        help_text="Score obtenido por el validador de imagen.",
    )
    image_min_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Score minimo de imagen",
        help_text="Umbral minimo de score requerido para validar la imagen.",
    )
    image_label_target = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID de etiqueta objetivo",
        help_text="ID de la etiqueta objetivo del modelo (ejemplo: bird).",
    )

    # ── Recompensa ────────────────────────────────────────────────────────────
    reward_withdrawal = models.ForeignKey(
        "reward.RewardWithdrawal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
        verbose_name="Retiro de recompensa",
        help_text="Retiro al que pertenece la recompensa de esta imagen.",
    )
    reward_rule = models.ForeignKey(
        "reward.RewardRule",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="images",
        verbose_name="Regla de recompensa aplicada",
        help_text="Regla que determinó el monto de recompensa para esta imagen.",
    )
    reward_amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Monto de recompensa (soles)",
        help_text="Monto en soles otorgado por esta imagen. Null si aún no se cobró.",
    )
    reward_claimed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cobro de recompensa",
        help_text="Fecha y hora en que se cobró la recompensa. Null si aún no se cobró.",
    )

    @property
    def is_reward_claimed(self) -> bool:
        return self.reward_claimed_at is not None

    class Meta:
        db_table = "images"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["uploaded_at"]),
            models.Index(fields=["captured_at"]),
            models.Index(fields=["device_type"]),
        ]

    def __str__(self) -> str:
        return self.file_name
