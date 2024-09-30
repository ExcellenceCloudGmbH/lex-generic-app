from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class TokenObtainPairWithUserSerializer(TokenObtainPairSerializer):
    """
    Serializer for obtaining JWT tokens with additional user information.

    This serializer extends the TokenObtainPairSerializer to include the
    username of the authenticated user in the response data.

    Methods
    -------
    validate(attrs)
        Validates and returns the token data along with the username.
    """
    def validate(self, attrs):
        """
        Validate and return token data with additional user information.

        Parameters
        ----------
        attrs : dict
            The attributes to validate.

        Returns
        -------
        dict
            The validated token data including the username.
        """
        data = super(TokenObtainPairWithUserSerializer, self).validate(attrs)
        data.update({'user': {'username': self.user.username}})
        return data


class TokenObtainPairWithUserView(TokenObtainPairView):
    """
    View for obtaining JWT tokens with additional user information.

    This view uses the TokenObtainPairWithUserSerializer to include the
    username of the authenticated user in the response data.

    Attributes
    ----------
    serializer_class : class
        The serializer class to use for validating and obtaining the token.
    """
    serializer_class = TokenObtainPairWithUserSerializer
