from django.urls import include, path

urlpatterns = [
    path("", include("apps.models.tag.api.routers")),
]
