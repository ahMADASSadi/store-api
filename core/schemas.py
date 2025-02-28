from graphene.types import ObjectType, Field, List, ID
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from core.models import User, OTP


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'phone_number', 'password']


class OTPType(DjangoObjectType):
    class Meta:
        model = OTP
        fields = ['id', 'user', 'otp_code', 'created_at']


class Query(ObjectType):
    all_users = List(UserType, description="Get all users")
    user_by_id = Field(UserType, id=ID(required=True),
                       description="Get user by ID")
    me = Field(UserType, id=ID(required=True), description="Get current user")
    all_otps = List(OTPType, description="Get all OTPs")
    otp_by_id = Field(OTPType, id=ID(required=True),
                      description="Get OTP by ID")

    def resolve_all_users(self, info):
        return User.objects.all()
