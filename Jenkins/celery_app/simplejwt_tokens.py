from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

# my_user=get_user_model()

def create_simplejwt_token_for_user(user):
    refresh_token = RefreshToken.for_user(user)
    tokens = {
        'access_token': str(refresh_token.access_token),
        'refresh_token': str(refresh_token)
    }
    return tokens
    