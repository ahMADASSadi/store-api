from rest_framework.routers import DefaultRouter

from admin_panel.auth_views import AdminAuthViewSet


router = DefaultRouter()
router.register(r"", AdminAuthViewSet, basename="admin")

urlpatterns = router.urls
