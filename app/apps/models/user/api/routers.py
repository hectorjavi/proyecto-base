from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()


router.register(r"users", viewsets.UserViewSet, basename="users")

urlpatterns = router.get_urls()
