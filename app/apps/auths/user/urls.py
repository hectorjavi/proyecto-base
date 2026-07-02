from django.urls import path

from apps.auths.user.api import viewsets

urlpatterns = [
    path("auth/token/", viewsets.LoginView.as_view(), name="token_obtain"),
    path(
        "auth/token/refresh/",
        viewsets.TokenRefreshViewDoc.as_view(),
        name="token_refresh",
    ),
    path(
        "auth/token/verify/", viewsets.TokenVerifyViewDoc.as_view(), name="token_verify"
    ),
    path(
        "auth/token/blacklist/",
        viewsets.TokenBlacklistViewDoc.as_view(),
        name="token_blacklist",
    ),
    path("auth/me/", viewsets.UserMeView.as_view(), name="user_me"),
    path(
        "auth/me/reset_password/",
        viewsets.UserMePassView.as_view(),
        name="user_me_reset_password",
    ),
]
