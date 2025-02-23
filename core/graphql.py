from graphql.execution.middleware import MiddlewareManager
from core.middlewares import AuthenticationMiddleware
from core.schemas import Query
from core.mutations import Mutation
from graphene.types import Schema


schema = Schema(query=Query, middleware=[
    MiddlewareManager(AuthenticationMiddleware())])
