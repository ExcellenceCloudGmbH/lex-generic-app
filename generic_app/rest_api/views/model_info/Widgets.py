from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from django.http import JsonResponse
from generic_app import models

class Widgets(APIView):
    """
    API view for handling widget-related requests.

    This view only allows GET requests and requires the requester to be
    authenticated either via API key or user authentication.
    """
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, *args, **kwargs):
        """
        Handle GET requests to retrieve widget structure.

        Parameters
        ----------
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        JsonResponse
            JSON response containing the widget structure.
        """
        return JsonResponse({"widget_structure": models.widget_structure})
