from graphene.types import Schema


from store.mutations import Mutation
from store.schemas import Query

schema = Schema(query=Query, mutation=Mutation)
