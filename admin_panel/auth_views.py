from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from admin_panel.serializers import AdminTokenObtainSerializer, AdminUserSerializer


User = get_user_model()


class AdminAuthViewSet(viewsets.ViewSet):
    @extend_schema(
        summary="Login (JWT) for staff users",
        description="Obtain JWT token pair (access and refresh) with credentials.",
        request=AdminTokenObtainSerializer,
        responses={
            200: OpenApiResponse(
                response=AdminTokenObtainSerializer,
                description="Returns access and refresh tokens."
            ),
            400: OpenApiResponse(description="Invalid credentials or input error")
        },
        examples=[
            OpenApiExample(
                "Example login request",
                value={"username": "admin_username",
                       "password": "admin_password"},
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """Authenticate a staff user and return JWT tokens."""
        serializer = AdminTokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Logout (JWT)",
        description="Blacklist the refresh token to log out the current user.",
        request={"type": "object", "properties": {"refresh": {
            "type": "string", "description": "Refresh token"}}},
        responses={
            200: OpenApiResponse(
                description="Logout successful.",
                examples=[OpenApiExample("Logout Response", value={
                                         "message": "Logged out successfully"})]
            ),
            400: OpenApiResponse(description="Invalid token or error during logout")
        }
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def logout(self, request):
        """Invalidate the refresh token to log out the user."""
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            RefreshToken(refresh_token).blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get current admin user",
        description="Retrieve details of the currently authenticated admin user.",
        responses={
            200: AdminUserSerializer,
            403: OpenApiResponse(description="Unauthorized access")
        }
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser, IsAuthenticated])
    def me(self, request):
        """Retrieve the currently logged-in admin user's details."""
        serializer = AdminUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
