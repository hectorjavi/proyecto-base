from django.conf import settings
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel, UUIDModel


class RewardRule(UUIDModel, TimeStampedModel):
    """
    Estrategia de recompensa: define el rango de score y el monto en soles.

    Regla: los rangos de reglas activas no deben solaparse.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Etiqueta descriptiva de la regla (ejemplo: 'Score alto').",
    )
    score_min = models.FloatField(
        verbose_name="Score mínimo",
        help_text="Valor mínimo de score (inclusivo) para aplicar esta regla.",
    )
    score_max = models.FloatField(
        verbose_name="Score máximo",
        help_text="Valor máximo de score (inclusivo) para aplicar esta regla.",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        verbose_name="Monto (soles)",
        help_text="Monto en soles que se otorga al usuario cuando su imagen cae en este rango. Soporta hasta 8 decimales (ej: 0.00000100).",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Solo las reglas activas se consideran al cobrar una recompensa.",
    )

    class Meta:
        db_table = "reward_rules"
        ordering = ["score_min"]
        verbose_name = "Regla de recompensa"
        verbose_name_plural = "Reglas de recompensa"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["score_min", "score_max"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.score_min}–{self.score_max}) → S/ {self.amount}"


class RewardWithdrawal(UUIDModel, TimeStampedModel):
    """
    Retiro de recompensas acumuladas del usuario.

    Acumula ImageReward hasta que el usuario lo cobra (is_paid=True).
    Una vez cobrado queda como histórico inmutable y se crea un nuevo
    retiro abierto para los siguientes cobros.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reward_withdrawals",
        verbose_name="Usuario",
        help_text="Usuario dueño del retiro.",
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0,
        verbose_name="Total acumulado (soles)",
        help_text="Suma de los montos de todas las recompensas de imágenes en este retiro.",
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Cobrado",
        help_text="Indica si el usuario ya cobró este retiro. Una vez True no puede modificarse.",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cobro",
        help_text="Fecha y hora en que el usuario cobró este retiro.",
    )

    class Meta:
        db_table = "reward_withdrawals"
        ordering = ["-created"]
        verbose_name = "Retiro de recompensas"
        verbose_name_plural = "Retiros de recompensas"
        indexes = [
            models.Index(fields=["user", "is_paid"]),
        ]

    def __str__(self) -> str:
        estado = "Cobrado" if self.is_paid else "Abierto"
        return f"{self.user_id} | S/ {self.total_amount} | {estado}"

    def pay(self) -> None:
        """Marca el retiro como cobrado. Idempotente si ya está pagado."""
        if self.is_paid:
            return
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save(update_fields=["is_paid", "paid_at", "modified"])


