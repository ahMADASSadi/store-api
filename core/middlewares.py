

class AuthenticationMiddleware:
    def resolve(self, next, root, info, **args):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        return next(root, info, **args)
