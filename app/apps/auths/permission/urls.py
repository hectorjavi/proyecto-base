from django.urls import include, path

urlpatterns = [
    path(
        "",
        include("apps.auths.permission.api.routers"),
    ),
]
