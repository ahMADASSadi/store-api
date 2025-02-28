from graphql.execution.middleware import MiddlewareManager
from graphene.types import Schema


from core.middlewares import AuthenticationMiddleware
from core.mutations import AuthMutation
from core.schemas import Query


schema = Schema(query=Query, mutation=[AuthMutation], middleware=[
    MiddlewareManager(AuthenticationMiddleware())])
