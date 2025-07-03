from rest_framework import serializers, viewsets

# --------------------------------------------------------------------------
#  Your existing base classes
# --------------------------------------------------------------------------

class RestApiModelSerializerTemplate(serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField()

    def get_short_description(self, obj):
        return str(obj)

    class Meta:
        model = None
        fields = "__all__"


class RestApiModelViewSetTemplate(viewsets.ModelViewSet):
    queryset = None
    serializer_class = None


# --------------------------------------------------------------------------
#  Constants
# --------------------------------------------------------------------------

ID_FIELD_NAME = 'id_field'
SHORT_DESCR_NAME = 'short_description'


# --------------------------------------------------------------------------
#  Enhanced ManyToMany field
# --------------------------------------------------------------------------

class ManyToManyListField(serializers.ListField):
    """
    - Serializes to a list of PKs
    - On input accepts:
        * the string "[]"
        * the list ["[]"]
        * a list of PKs (ints or digit-strings)
    """
    def __init__(self, queryset, **kwargs):
        child = serializers.PrimaryKeyRelatedField(queryset=queryset)
        super().__init__(child=child, **kwargs)

    def to_internal_value(self, data):
        # 1) If client sent the raw string "[]", clear the relation
        if isinstance(data, str) and data.strip() == '[]':
            return []
        # 2) If client sent ["[]"], also treat as clear
        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], str) and data[0].strip() == '[]':
            return []
        # 3) Otherwise, coerce digit-strings into ints, then validate as PKs
        if isinstance(data, list):
            coerced = []
            for item in data:
                if isinstance(item, str) and item.isdigit():
                    coerced.append(int(item))
                else:
                    coerced.append(item)
            return super().to_internal_value(coerced)
        # 4) Fallback (will raise “not a list” if it’s neither str nor list)
        return super().to_internal_value(data)

    def to_representation(self, data):
        # Always return a plain list of PKs
        iterable = data.all() if hasattr(data, 'all') else data
        return [self.child.to_representation(item) for item in iterable]


# --------------------------------------------------------------------------
#  Your dynamic serializer builder
# --------------------------------------------------------------------------

def model2serializer(model, fields=None):
    """
    Dynamically build a ModelSerializer for model that:
      - Exposes all fields (or all concrete/FK fields if None)
      - Ensures the real PK field (model._meta.pk.name) is in the output
      - Adds id_field (read-only) whose value is the name of that PK field
      - Adds short_description
      - Swaps out any included M2M for our enhanced ListField
    """
    # 1) determine fields
    if fields is None:
        fields = [f.name for f in model._meta.fields]
    pk_name = model._meta.pk.name
    if pk_name not in fields:
        fields.append(pk_name)

    # 2) id_field = the NAME of your PK column
    id_field = serializers.ReadOnlyField(default=pk_name)

    # 3) assemble attrs
    attrs = {
        ID_FIELD_NAME: id_field,
        'Meta': type(
            'Meta',
            (RestApiModelSerializerTemplate.Meta,),
            {
                'model': model,
                'fields': fields + [ID_FIELD_NAME, SHORT_DESCR_NAME],
            }
        )
    }

    # 4) override M2M fields you’re exposing
    for m2m in model._meta.many_to_many:
        if m2m.name in fields:
            attrs[m2m.name] = ManyToManyListField(
                queryset=m2m.remote_field.model.objects.all()
            )

    # 5) build & return the Serializer subclass
    serializer_name = f"{model._meta.model_name.capitalize()}Serializer"
    return type(serializer_name, (RestApiModelSerializerTemplate,), attrs)