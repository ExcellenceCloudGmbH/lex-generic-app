from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from generic_app.rest_api.views.permissions.UserPermission import UserPermission


class ModelEntryProviderMixin:
    """
    Mixin class to provide model entry related functionalities.

    This mixin sets the permission classes and provides methods to get
    the queryset and serializer class based on the model container.

    Attributes
    ----------
    permission_classes : list
        List of permission classes required for accessing the views.
    """
    permission_classes = [HasAPIKey | IsAuthenticated, UserPermission]

    def get_queryset(self):
        """
        Get the queryset for the model.

        Returns
        -------
        QuerySet
            The queryset for the model class specified in the model container.
        """
        return self.kwargs['model_container'].model_class.objects.all()

    def get_serializer_class(self):
        """
        Get the serializer class for the model.

        Returns
        -------
        Serializer
            The serializer class specified in the model container.
        """
        return self.kwargs['model_container'].obj_serializer