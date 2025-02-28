from graphql_jwt import (ObtainJSONWebToken, Verify, Refresh)
from graphene.types import ObjectType


class AuthMutation(ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
