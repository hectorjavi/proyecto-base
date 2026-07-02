from django.urls import include, path

# GET, POST, PUT, PATCH, DELETE
urlpatterns = [
    path("", include("apps.models.image.api.routers")),
]
