from django.http import JsonResponse


def health(request):
    """Liveness probe for Docker / orchestrators. No authentication required."""
    return JsonResponse({"status": "ok"})
