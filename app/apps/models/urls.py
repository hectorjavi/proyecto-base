from django.urls import include, path

urlpatterns = [
    # path("", include("apps.models.user.urls")),  # desactivado temporalmente
    path("", include("apps.models.image.urls")),
    path("", include("apps.models.tag.urls")),
    path("", include("apps.models.reward.urls")),
    path("", include("apps.models.models_detectors.urls")),
]
