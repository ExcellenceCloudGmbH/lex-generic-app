import os
from io import BytesIO

from django.http import FileResponse, JsonResponse
from django_sharepoint_storage.SharePointContext import SharePointContext
from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey


class FileDownloadView(APIView):
    """
    API view for downloading files.

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
        Handle GET requests to download a file.

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
        FileResponse or JsonResponse
            A response containing the file to be downloaded or a JSON response with the download URL.
        """
        model = kwargs['model_container'].model_class
        shrp_ctx = SharePointContext()
        instance = model.objects.filter(pk=request.query_params['pk'])[0]
        file = instance.__getattribute__(request.query_params['field'])

        if os.getenv("KUBERNETES_ENGINE", "NONE") == "NONE":
            # TODO, not compatible with production environment
            file_url = file.url if not file.url.startswith('/') else file.url[1:]
        else:
            file_url = file.url

        if os.getenv("STORAGE_TYPE") == "SHAREPOINT":
            file = shrp_ctx.ctx.web.get_file_by_server_relative_path(get_server_relative_path(file.url)).execute_query()
            binary_file = file.open_binary(shrp_ctx.ctx, get_server_relative_path(file_url))
            bytesio_object = BytesIO(binary_file.content)
            return FileResponse(bytesio_object)
        elif os.getenv("STORAGE_TYPE") == "GCS":
            return JsonResponse({"download_url": file_url})
        else:
            return FileResponse(open(file_url, 'rb'))