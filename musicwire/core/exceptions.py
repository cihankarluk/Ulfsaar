from rest_framework.exceptions import ValidationError


class ValidationError(ValidationError):
    code = 'VALIDATION_ERROR'


class AddTracksError(ValidationError):
    code = 'ADD_TRACKS_ERROR'
