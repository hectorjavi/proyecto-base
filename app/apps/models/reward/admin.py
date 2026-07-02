import json
import re
from django.contrib import admin
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path

from .models import RewardRule, RewardWithdrawal

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _extract_withdrawal_uuid(text: str) -> str | None:
    if not text or not isinstance(text, str):
        return None
    m = _UUID_RE.search(text.strip())
    return m.group(0) if m else None


@admin.register(RewardRule)
class RewardRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "score_min", "score_max", "amount", "is_active", "created")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("score_min",)


class ImageInline(admin.TabularInline):
    """Imágenes cuya recompensa pertenece a este retiro."""

    from apps.models.image.models import Image

    model = Image
    fk_name = "reward_withdrawal"
    extra = 0
    fields = ("file_name", "reward_rule", "reward_amount", "reward_claimed_at")
    readonly_fields = ("file_name", "reward_rule", "reward_amount", "reward_claimed_at")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(RewardWithdrawal)
class RewardWithdrawalAdmin(admin.ModelAdmin):
    change_list_template = "admin/reward/rewardwithdrawal/change_list.html"
    list_display = ("id", "user", "total_amount", "is_paid", "paid_at", "created")
    list_filter = ("is_paid",)
    search_fields = ("user__email",)
    ordering = ("-created",)
    readonly_fields = ("total_amount", "is_paid", "paid_at", "created", "modified")
    inlines = [ImageInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        custom = [
            path(
                "scan-pay/",
                self.admin_site.admin_view(self.scan_pay_view),
                name="%s_%s_scan_pay" % info,
            ),
        ]
        return custom + super().get_urls()

    def scan_pay_view(self, request):
        """GET: página con lector QR. POST: marca el retiro como cobrado (misma lógica que API pay)."""
        if request.method == "POST":
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return JsonResponse(
                    {"ok": False, "error": "Cuerpo JSON inválido."},
                    status=400,
                )

            raw = payload.get("withdrawal_id", "")
            uuid_str = _extract_withdrawal_uuid(str(raw))
            if not uuid_str:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": "No se encontró un UUID de retiro válido en el código.",
                    },
                    status=400,
                )

            try:
                withdrawal = RewardWithdrawal.objects.get(pk=uuid_str)
            except RewardWithdrawal.DoesNotExist:
                return JsonResponse(
                    {"ok": False, "error": "Retiro no encontrado."},
                    status=404,
                )

            if withdrawal.is_paid:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": "Este retiro ya fue cobrado anteriormente.",
                    },
                    status=400,
                )

            if withdrawal.total_amount <= 0:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": "No hay monto acumulado para cobrar.",
                    },
                    status=400,
                )

            withdrawal.pay()

            return JsonResponse(
                {
                    "ok": True,
                    "withdrawal_id": str(withdrawal.pk),
                    "total_amount": str(withdrawal.total_amount),
                    "user": str(withdrawal.user_id),
                }
            )

        context = {
            **self.admin_site.each_context(request),
            "title": "Cobrar retiro con código QR",
            "opts": self.model._meta,
        }
        return TemplateResponse(
            request,
            "admin/reward/rewardwithdrawal/scan_pay.html",
            context,
        )
