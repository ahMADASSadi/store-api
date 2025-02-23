from graphene_django.types import DjangoObjectType
from graphene.types import ObjectType, Field, List, Int, String

from graphql.error import GraphQLError

from store.models import Product, Category, ProductImage


class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "product"]


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "category", "description"]


class Query(ObjectType):
    all_products = List(ProductType, description="Get all products")
    product_by_id = Field(ProductType, id=Int(required=True),
                          description="Get product by ID")

    all_categories = List(CategoryType, description="Get all categories")
    category_by_id = Field(CategoryType, id=Int(required=True),
                           description="Get category by ID")

    product_images_by_product_id = List(ProductImageType, product_id=Int(required=True),
                                        description="Get product images by product ID")

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_product_by_id(self, info, id):
        return Product.objects.get(pk=id)

    def resolve_all_categories(self, info):
        return Category.objects.all()

    def resolve_category_by_id(self, info, id):
        return Category.objects.get(pk=id)

    def resolve_product_images_by_product_id(self, info, product_id):
        return ProductImage.objects.filter(product_id=product_id)
