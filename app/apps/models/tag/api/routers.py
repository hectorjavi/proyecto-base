from rest_framework.routers import DefaultRouter

from .viewsets import TagViewSet

router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tags")

urlpatterns = router.get_urls()
