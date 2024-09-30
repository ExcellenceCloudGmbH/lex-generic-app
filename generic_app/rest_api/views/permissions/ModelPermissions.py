from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

class ModelPermissions(APIView):
    """
    API view to handle model permissions.

    This view restricts access to authenticated users or those with an API key.
    It only allows GET requests.

    Attributes
    ----------
    http_method_names : list
        Allowed HTTP methods for this view.
    permission_classes : list
        Permissions required to access this view.
    """
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve model restrictions for the user.

        Parameters
        ----------
        request : Request
            The request object.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A response object containing the model restrictions.
        """
        model_container = self.kwargs['model_container']
        user = request.user

        model_restrictions = {model_container.id: model_container.get_general_modification_restrictions_for_user(user)}

        return Response(model_restrictions)