from django.urls import path

from graphene_django.views import GraphQLView

from store.graphql import schema

from rest_framework.routers import DefaultRouter

from store.views import AddressViewSet, CartItemViewSet, CartViewSet, ProductViewSet, ReviewViewSet, UserProfileViewSet


user_profile_router = DefaultRouter()

user_profile_router.register(r"profile", UserProfileViewSet, basename="user")

user_profile_router.register(r"address", AddressViewSet, basename="address")

# user_profile_router.register(r"carts", CartViewSet, basename="carts")

# user_profile_router.register(
#     r"cart-items", CartItemViewSet, basename="cart-items")

product_router = DefaultRouter()

product_router.register(
    r"product", ProductViewSet, basename="product")

product_router.register(
    r"review", ReviewViewSet, basename="review")

urlpatterns = [
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]

urlpatterns += user_profile_router.urls + product_router.urls
