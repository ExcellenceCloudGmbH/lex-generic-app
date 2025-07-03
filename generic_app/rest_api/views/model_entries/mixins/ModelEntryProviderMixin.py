from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from django.contrib.auth.models import User

from generic_app.rest_api.views.permissions.UserPermission import UserPermission

# --- UserModelSerializer Serializer ---
class UserModelSerializer(serializers.ModelSerializer):
    id_field = serializers.ReadOnlyField(default=User._meta.pk.name)
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__"

    def get_short_description(self, obj):
        return f"{obj.first_name} {obj.last_name} - {obj.email}"

class ModelEntryProviderMixin:
    permission_classes = [HasAPIKey | IsAuthenticated, UserPermission]

    def get_queryset(self):
        return self.kwargs['model_container'].model_class.objects.all()

    def get_serializer_class(self):
        model_class = self.kwargs['model_container'].model_class
        if issubclass(model_class, User):
            return UserModelSerializer
        else:
            return self.kwargs['model_container'].obj_serializer
