from django.contrib.auth.backends import ModelBackend
from .models import CustomUser
from django.core.exceptions import ObjectDoesNotExist

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to authenticate by email if username is not provided or is email-like
        if username is None:
            username = kwargs.get('email')

        try:
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None 