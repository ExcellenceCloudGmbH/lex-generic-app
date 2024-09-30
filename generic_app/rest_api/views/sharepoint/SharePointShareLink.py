import os

from django_sharepoint_storage.SharePointContext import SharePointContext
from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from django.http import JsonResponse


class SharePointShareLink(APIView):
    """
    API view to generate a SharePoint share link for a given file.

    Attributes
    ----------
    model_collection : None
        Placeholder for model collection, not used in this implementation.
    http_method_names : list of str
        Allowed HTTP methods for this view.
    permission_classes : list
        Permissions required to access this view.
    """
    model_collection = None
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to generate a SharePoint share link.

        Parameters
        ----------
        request : HttpRequest
            The request object containing query parameters.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments, including 'model_container'.

        Returns
        -------
        JsonResponse
            JSON response containing the generated share link.
        """
        model = kwargs['model_container'].model_class
        shrp_ctx = SharePointContext()
        instance = model.objects.filter(pk=request.query_params['pk'])[0]
        file = instance.__getattribute__(request.query_params['field'])

        file = shrp_ctx.ctx.web.get_file_by_server_relative_path(get_server_relative_path(file.url)).get().execute_query()
        share_link = str(os.getenv(
            'FILE_PREVIEW_LINK_BASE')) + "sourcedoc={" + file.unique_id + "}&action=default&mobileredirect=true"

        return JsonResponse({"share_link": share_link})