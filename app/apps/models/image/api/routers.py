from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()

router.register(r"images", viewsets.ImageViewSet, basename="images")

urlpatterns = router.get_urls()
