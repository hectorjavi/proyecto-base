from rest_framework.routers import DefaultRouter

from .viewsets import RewardWithdrawalViewSet

router = DefaultRouter()
router.register(r"rewards/withdrawals", RewardWithdrawalViewSet, basename="reward-withdrawals")

urlpatterns = router.urls
