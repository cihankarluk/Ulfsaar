from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from rest_framework import status

from musicwire.account.models import UserProfile

EXEMPT_URLS = settings.EXEMPT_URLS


def exempt_url_check(path):
    """Control over url if it accessible for everyone."""
    permission = [
        path.startswith(url_) for url_ in EXEMPT_URLS
    ]
    return any(permission)


class UserAuthenticationMiddleware(MiddlewareMixin):
    @staticmethod
    def display_error_message(msg, **kwargs):
        data = {
            'status_code': status.HTTP_401_UNAUTHORIZED,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }
        return JsonResponse(data, status=401)

    def process_view(self, request, view_func, view_args, view_kwargs):
        token = request.META.get('HTTP_TOKEN')
        content_type = request.META.get('CONTENT_TYPE')
        request_method = request.META.get('REQUEST_METHOD')
        check_url = not exempt_url_check(request.path)

        try:
            user = UserProfile.objects.get(
                token=token
            )
        except UserProfile.DoesNotExist:
            user = None

        if not user and check_url:
            return self.display_error_message(
                'The API key does not have permission on this endpoint.')

        post_conditions = all([
            request_method == 'POST',
            content_type != 'application/json',
            content_type != 'application/x-www-form-urlencoded'])  # admin side

        if post_conditions:
            return self.display_error_message(
                'Not valid Content-Type',
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                status_text='Unsupported Media Type'
            )

        setattr(request, 'account', user)
