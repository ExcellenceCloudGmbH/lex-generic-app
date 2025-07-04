from django.db.models import (
    ForeignKey, ManyToManyField, CharField,
    IntegerField, FloatField, BooleanField,
    DateField, DateTimeField, FileField, ImageField,
    AutoField, JSONField
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from generic_app.generic_models.fields.Bokeh_field import BokehField
from generic_app.generic_models.fields.HTML_field import HTMLField
from generic_app.generic_models.fields.PDF_field import PDFField
from generic_app.generic_models.fields.XLSX_field import XLSXField
from generic_app.generic_models.upload_model import CalculateField, IsCalculatedField
from generic_app.rest_api.views.permissions.UserPermission import UserPermission

DJANGO_FIELD2TYPE_NAME = {
    ForeignKey: 'foreign_key',
    ManyToManyField: 'many_to_many',
    CharField: 'string',          # explicitly support CharField
    IntegerField: 'int',
    FloatField: 'float',
    BooleanField: 'boolean',
    DateField: 'date',
    DateTimeField: 'date_time',
    FileField: 'file',
    PDFField: 'pdf_file',
    XLSXField: 'xlsx_file',
    HTMLField: 'html',
    BokehField: 'bokeh',
    ImageField: 'image_file',
    CalculateField: 'calculate',
    IsCalculatedField: 'is_calculated',
    JSONField: 'json',
}

DEFAULT_TYPE_NAME = 'string'

def create_field_info(field):
    default_value = None
    if field.get_default() is not None:
        default_value = field.get_default()

    field_type = type(field)
    type_name = DJANGO_FIELD2TYPE_NAME.get(field_type, DEFAULT_TYPE_NAME)

    additional_info = {}

    # relations: include target and any limit_choices_to
    if field_type in (ForeignKey, ManyToManyField):
        additional_info['target'] = field.remote_field.model._meta.model_name
        additional_info['limit_choices_to'] = field.remote_field.limit_choices_to

    # choices (for CharField or any field with choices)
    if getattr(field, 'choices', None):
        # turn each (value, label) into a dict for clarity
        additional_info['choices'] = [
            {'id': val, 'name': label}
            for val, label in field.choices
        ]

    return {
        'name': field.name,
        'readable_name': field.verbose_name.title(),
        'type': type_name,
        # auto-fields (AutoField) are not editable
        'editable': field.editable and field_type is not AutoField,
        'required': not (field.null or default_value is not None),
        'default_value': default_value,
        **additional_info
    }


class Fields(APIView):
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated, UserPermission]

    def get(self, *args, **kwargs):
        model = kwargs['model_container'].model_class
        fields = list(model._meta.fields) + list(model._meta.many_to_many)
        field_info = {
            'fields': [create_field_info(f) for f in fields],
            'id_field': model._meta.pk.name
        }
        return Response(field_info)
