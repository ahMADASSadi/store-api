from graphene.types import Mutation, ObjectType, String, Int, Field


from store.schemas import ProductType, CategoryType, ProductImageType
from store.models import Product, Category, ProductImage


class CreateProduct(Mutation):
    class Arguments:
        title = String(required=True)
        unit_price = Int(required=True)
        stock = Int(required=True)
        category_id = Int(required=True)
        description = String(required=True)

    product = Field(ProductType)

    def mutate(self, info, title, unit_price, stock, category_id, description):
        product = Product.objects.create(
            title=title, unit_price=unit_price, stock=stock, category_id=category_id, description=description)
        return CreateProduct(product=product)


class Mutation(ObjectType):
    create_product = CreateProduct.Field()
