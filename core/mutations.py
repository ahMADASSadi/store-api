from graphene.types import ObjectType
from graphql_jwt import (ObtainJSONWebToken, Verify, Refresh)


class AuthMutation(ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
