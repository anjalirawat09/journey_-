from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.http import HttpResponse

class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # List of paths to bypass token validation
        self.bypass_paths = [
            '/journey/addtojob-journey-update/',
            '/journey/addnextevent-by-camapignstatus/',

        ]

    def __call__(self, request):
        # Check if the request path should bypass token validation
        if any(request.path.startswith(path) for path in self.bypass_paths):
            return self.get_response(request)
    # def __call__(self, request):
        token = request.headers.get('Authorization')

        if token:
            # Check if the token format is valid (starts with "Bearer ")
            if not token.startswith('Bearer '):
                return self.invalid_token_response(request)

            # Extract the token after removing "Bearer "
            token = token.split('Bearer ')[1].strip()

            try:
                JWT_authenticator = JWTAuthentication()
                response = JWT_authenticator.authenticate(request)
                if response:
                    UserData, token = response
                    request.UserData = UserData
                    request.token = token
                    return self.get_response(request)
                else:
                    return self.invalid_token_response(request)
            except InvalidToken:
                return self.invalid_token_response(request)
        else:
            return self.unauthorized_response(request) 

    def invalid_token_response(self, request):
        return HttpResponse(status=401, content='Invalid token', content_type='text/plain')

    def unauthorized_response(self, request):
        return HttpResponse(status=401, content='Unauthorized: Token is missing', content_type='text/plain')