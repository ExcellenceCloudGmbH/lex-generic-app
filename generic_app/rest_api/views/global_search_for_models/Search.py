from django.contrib.postgres.search import SearchVector
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from generic_app.rest_api.model_collection.model_collection import ModelCollection
from generic_app.rest_api.views.permissions.UserPermission import UserPermission

EXCLUDED_MODELS = {'calculationdashboard', 'user', 'group', 'permission', 'contenttype', 'userchangelog',
                   'calculationlog', 'log', 'streamlit'}
EXCLUDED_TYPES = {'FloatField', 'BooleanField', 'IntegerField', "FileField", "ForeignKey", "XLSXField", "PDFField", "ImageField"}


class Search(APIView):
    """
    API view for searching across multiple models.

    This view allows authenticated users to search for a query string across
    various models, excluding certain models and field types.

    Attributes
    ----------
    permission_classes : list
        List of permission classes that are required to access this view.
    model_collection : ModelCollection
        Collection of models to be searched.

    Methods
    -------
    get(request, *args, **kwargs)
        Handles GET requests to perform the search.
    """
    permission_classes = [HasAPIKey | IsAuthenticated]
    model_collection: ModelCollection = None

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to perform the search.

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
            A Response object containing the search results or a message indicating no matches were found.
        """
        query = self.kwargs['query']
        allMatches = []
        for model in self.model_collection.all_containers:
            temp_view = APIView(kwargs={'model_container': model})
            if model.id not in EXCLUDED_MODELS and UserPermission().has_permission(request=request, view=temp_view):
                fields = model.model_class._meta.get_fields(include_parents=False)
                tempMatch = model.model_class.objects.annotate(search=SearchVector(*[f.name for f in fields if
                                                                                     f.get_internal_type() not in EXCLUDED_TYPES])).filter(
                    search=query)
                for match in tempMatch:
                    if UserPermission().has_object_permission(request=request, view=temp_view, obj=match):
                        matchObj = {"id": str(match.pk), "type": model.title, "model": model.id,
                                    "url": f'/{model.id}/{match.pk}/show', "content": {
                                "id": str(match.pk),
                                "label": 'Model: ' + model.title ,
                                "description": str(match)}}
                        allMatches.append(matchObj)

        if allMatches:
            result = {"data": allMatches, "total": len(allMatches)}
            return Response(result)
        else:
            return Response("No match found")
