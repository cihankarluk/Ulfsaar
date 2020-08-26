from rest_framework.response import Response
from rest_framework.views import APIView

from musicwire.core.exceptions import UsernameAlreadyExists, UserSignInFail
from musicwire.account.models import UserProfile
from musicwire.account.serializers import UserCreateSerializer, UserSignInSerializer


class UserSignUp(APIView):
    def post(self, request, *args, **kwargs):
        serialized = UserCreateSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        username, password = valid_data['username'], valid_data['password']

        try:
            UserProfile.objects.get(username=username)
            raise UsernameAlreadyExists('Please try another username.')
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(
                username=username,
                password=password
            )

        return Response(status=201)


class UserSignIn(APIView):
    def post(self, request, *args, **kwargs):
        serialized = UserSignInSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        username, password = valid_data['username'], valid_data['password']

        try:
            user = UserProfile.objects.get(username=username, password=password)
            return Response({'token': user.token}, status=200)
        except UserProfile.DoesNotExist:
            raise UserSignInFail('Please control username or password.')
