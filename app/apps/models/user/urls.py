from django.urls import include, path

# GET, POST, PUT, PATCH, DELETE
urlpatterns = [
    path("", include("apps.models.user.api.routers")),
]
