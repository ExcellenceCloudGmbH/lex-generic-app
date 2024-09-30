from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from generic_app.rest_api.views.model_entries.filter_backends import PrimaryKeyListFilterBackend
from generic_app.rest_api.views.model_entries.mixins.ModelEntryProviderMixin import ModelEntryProviderMixin


class ManyModelEntries(ModelEntryProviderMixin, GenericAPIView):
    """
    A view that provides methods to handle multiple model entries.

    This view supports GET, PATCH, and DELETE HTTP methods to retrieve, update, 
    and delete multiple model entries respectively. It uses the 
    `PrimaryKeyListFilterBackend` to filter the queryset based on primary keys.
    """
    filter_backends = [PrimaryKeyListFilterBackend]

    def get_filtered_query_set(self):
        """
        Get the filtered queryset after applying object-level permissions.

        This method filters the queryset based on the request and checks 
        object-level permissions for each entry in the filtered queryset.

        Returns
        -------
        QuerySet
            The filtered queryset with object-level permissions applied.
        """
        filtered_qs = self.filter_queryset(self.get_queryset())
        # we check user-permissions object-wise; our permission class UserPermission automatically
        #   differentiates between read - and modify-restrictions, depending on the http-method
        for entry in filtered_qs:
            self.check_object_permissions(self.request, entry)
        return filtered_qs

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve multiple model entries.

        Parameters
        ----------
        request : Request
            The HTTP request object.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            The HTTP response containing serialized data of the retrieved entries.
        """
        queryset = self.get_filtered_query_set()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests to update multiple model entries.

        Parameters
        ----------
        request : Request
            The HTTP request object.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            The HTTP response containing primary keys of the updated entries.
        """
        queryset = self.get_filtered_query_set()
        serializer = self.get_serializer(queryset, data=request.data, partial=True, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        pk_name = self.kwargs['model_container'].pk_name
        return Response([d[pk_name] for d in serializer.data])

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests to delete multiple model entries.

        Parameters
        ----------
        request : Request
            The HTTP request object.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            The HTTP response containing primary keys of the deleted entries.
        """
        queryset = self.get_filtered_query_set()
        ids = list(queryset.values_list('pk', flat=True))
        queryset.delete()
        return Response(ids)
