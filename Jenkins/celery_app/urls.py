from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from celery_app.views import (
    home_add,
    home_sub,
    check_result,
    contact,
    RoleAssignmentViewSet,
    LoginView,
    CheckAccess,
    GetAccessTokenFromStaging,
)

router = DefaultRouter()
router.register(r"temporary-roles", RoleAssignmentViewSet, basename="temporary-role")
router.register(r"testing-roles", CheckAccess, basename="testing-role")
router.register(r"token", GetAccessTokenFromStaging, basename="get_token")

urlpatterns = [
    path("home/", home_add, name="home"),
    path("home_sub/", home_sub, name="home_sub"),
    path("check_result/<str:task_id>/", check_result, name="check_result"),
    path("contact/", contact, name="contact"),
    # Api
    path("", include(router.urls)),
    
    # Tokens
    path("token-create/", TokenObtainPairView.as_view(), name="token_create"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token-verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # Login
    path('login/', LoginView.as_view(), name="login"),
    

]
