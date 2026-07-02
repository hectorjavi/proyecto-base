from django.urls import include, path

from .api.routers import urlpatterns as reward_router_urls

urlpatterns = [
    path("", include(reward_router_urls)),
]
