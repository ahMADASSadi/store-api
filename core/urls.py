from rest_framework.routers import DefaultRouter

from core.views import AuthenticationViewSet, UserViewSet


router = DefaultRouter()
router.register(r"", AuthenticationViewSet, basename="auth")


router.register(r"user", UserViewSet, basename='user')
urlpatterns = router.urls
