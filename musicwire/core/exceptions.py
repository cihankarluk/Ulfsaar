from rest_framework import status
from rest_framework.exceptions import ValidationError


class ValidationError(ValidationError):
    code = 'VALIDATION_ERROR'


class AuthenticationFail(ValidationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = 'AUTHENTICATION_FAIL'


class UsernameAlreadyExists(ValidationError):
    code = 'USERNAME_ALREADY_EXISTS'


class UserSignInFail(ValidationError):
    code = 'USER_SIGN_IN_ERROR'


class AddTracksError(ValidationError):
    code = 'ADD_TRACKS_ERROR'


class ProviderDoesNotExists(ValidationError):
    code = 'PROVIDER_DOES_NOT_EXISTS'


class ProviderResponseError(ValidationError):
    code = 'PROVIDER_RESPONSE_ERROR'


class AllTracksAlreadyProcessed(ValidationError):
    code = 'ALL_TRACKS_ALREADY_PROCESSED'


class AllPlaylistsAlreadyProcessed(ValidationError):
    code = 'ALL_PLAYLISTS_ALREADY_PROCESSED'
