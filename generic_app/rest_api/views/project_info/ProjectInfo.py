from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
import os


class ProjectInfo(APIView):
    """
    API view to retrieve project information.

    This view requires the requester to be authenticated either via API key or
    standard authentication methods.

    Attributes
    ----------
    permission_classes : list
        List of permission classes that are required to access this view.
    """
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, *args, **kwargs):
            """
        Handle GET requests to retrieve project information.

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
            A response object containing the project information.
        """
            result = {"project_name": os.getenv("LEX_SUBMODEL_NAME"),
                      "branch_name": os.getenv("LEX_SUBMODEL_BRANCH"),
                      "environment": os.getenv("DEPLOYMENT_ENVIRONMENT")}
            return Response(result)