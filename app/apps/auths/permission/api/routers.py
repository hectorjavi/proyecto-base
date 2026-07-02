from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()

router.register(r"permissions", viewsets.PermissionViewSet, basename="permissions")

urlpatterns = router.urls
