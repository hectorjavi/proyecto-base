from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthAnonRateThrottle(AnonRateThrottle):
    scope = "auth"


class PasswordChangeUserRateThrottle(UserRateThrottle):
    scope = "password_change"
