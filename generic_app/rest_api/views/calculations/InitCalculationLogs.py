import os

from django_sharepoint_storage.SharePointContext import SharePointContext
from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from django.http import JsonResponse

from generic_app.submodels.CalculationLog import CalculationLog
from generic_app.submodels.UserChangeLog import UserChangeLog


class InitCalculationLogs(APIView):
    """
    API view to initialize and fetch calculation logs.

    This view handles GET requests to fetch logs from UserChangeLog and CalculationLog
    based on the provided calculation record and calculation ID.

    Attributes
    ----------
    http_method_names : list of str
        Allowed HTTP methods for this view.
    permission_classes : list
        Permissions required to access this view.
    """
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to fetch calculation logs.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        JsonResponse
            A JSON response containing the fetched logs.
        """
        calculation_record = request.query_params['calculation_record']
        calculation_id = request.query_params['calculation_id']

        messages = []

        # Fetch messages from UserChangeLog
        queryset_ucl = UserChangeLog.objects.filter(calculation_record=calculation_record,
                                                    calculationId=calculation_id).only('timestamp', 'message')
        messages.extend(f"{message.timestamp} {message.message}" for message in queryset_ucl)

        # Fetch messages from CalculationLog
        queryset_calc = CalculationLog.objects.filter(calculation_record=calculation_record,
                                                      calculationId=calculation_id).only('timestamp', 'message')
        messages.extend(f"{message.timestamp} {message.message}" for message in queryset_calc)

        return JsonResponse({"logs": "\n".join(messages)})