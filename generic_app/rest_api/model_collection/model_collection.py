import typing

from django.db.models import Model

from generic_app.generic_models.ModelModificationRestriction import ModelModificationRestriction
from generic_app.generic_models.Process import Process
from generic_app.generic_models.html_report import HTMLReport
from generic_app.rest_api.serializers import model2serializer

foreign_key_name = 'ForeignKey'
many_to_many_name = 'ManyToManyField'
one_to_one_name = 'OneToOneField'


def get_relation_fields(model):
    """
    Get the relation fields of a given model.

    Parameters
    ----------
    model : Model
        The Django model to inspect.

    Returns
    -------
    list
        A list of relation fields in the model.
    """
    relation_field_types = {foreign_key_name, one_to_one_name, many_to_many_name}
    return [field for field in model._meta.get_fields() if
            field.get_internal_type() in relation_field_types and not field.one_to_many]


def title_for_model(model):
    """
    Get the title for a given model.

    Parameters
    ----------
    model : Model
        The Django model to get the title for.

    Returns
    -------
    str
        The title of the model.
    """
    # TODO: add new way of defining custom readable name: e.g. via custom "meta"-class like "class CustomDefinitions"
    #   containing an attribute "readable_name"
    return model._meta.verbose_name.title()


class ModelContainer:
    """
    Container for a Django model with additional metadata and functionality.

    Parameters
    ----------
    model_class : type
        The Django model class.
    process_admin : object
        The process admin object associated with the model.
    models2containers : dict
        A dictionary mapping models to their containers.

    Attributes
    ----------
    model_class : type
        The Django model class.
    id : str
        The ID of the model.
    title : str
        The title of the model.
    process_admin : object
        The process admin object associated with the model.
    _models2containers : dict
        A dictionary mapping models to their containers.
    dependent_model_containers : set
        A set of dependent model containers.
    obj_serializer : object
        The serializer for the model objects.
    """

    def __init__(self, model_class, process_admin, models2containers) -> None:
        if hasattr(model_class, '_meta'):
            super().__init__()
            self.model_class = model_class
            self.id = self.model_class._meta.model_name
            self.title = title_for_model(self.model_class)
            self.process_admin = process_admin
            self._models2containers = models2containers
            self._models2containers[self.model_class] = self

            self.dependent_model_containers: typing.Set[ModelContainer] = set()

            self.obj_serializer = model2serializer(self.model_class,
                                                   self.process_admin.get_fields_in_table_view(self.model_class))
        else:
            super().__init__()
            self.model_class = model_class
            self.id = self.model_class.__name__.lower()
            self.title = self.model_class.__name__
            self.process_admin = process_admin
            self._models2containers = models2containers
            self._models2containers[self.model_class] = self

            self.dependent_model_containers: typing.Set[ModelContainer] = set()

            self.obj_serializer = None

    def get_modification_restriction(self):
        """
        Get the modification restriction for the model.

        Returns
        -------
        ModelModificationRestriction
            The modification restriction for the model.
        """
        return getattr(self.model_class, 'modification_restriction', ModelModificationRestriction())

    def get_general_modification_restrictions_for_user(self, user):
        """
        Get the general modification restrictions for a user.

        Parameters
        ----------
        user : User
            The user to check restrictions for.

        Returns
        -------
        dict
            A dictionary with general modification restrictions for the user.
        """
        modification_restriction = self.get_modification_restriction()
        return {
            'can_read_in_general': modification_restriction.can_read_in_general(user, None),
            'can_modify_in_general': modification_restriction.can_modify_in_general(user, None),
            'can_create_in_general': modification_restriction.can_create_in_general(user, None),
            'can_delete_in_general': modification_restriction.can_delete_in_general(user, None)
        }

    @property
    def pk_name(self):
        """
        Get the primary key name of the model.

        Returns
        -------
        str or None
            The primary key name of the model, or None if not applicable.
        """
        if hasattr(self.model_class, '_meta'):
            return self.model_class._meta.pk.name
        else:
            return None

    def read_dependencies(self):
        """
        Read and set up dependencies for the model.
        """
        if hasattr(self.model_class, '_meta'):
            for field in get_relation_fields(self.model_class):
                other_model = field.remote_field.model
                other_container = self._models2containers[other_model]
                other_container.dependent_model_containers.add(self)

                if field.get_internal_type() == many_to_many_name:
                    self.dependent_model_containers.add(other_container)


def create_model_containers(models2admins):
    """
    Create model containers from a dictionary of models to admins.

    Parameters
    ----------
    models2admins : dict
        A dictionary mapping models to their admin objects.

    Returns
    -------
    tuple
        A tuple containing two dictionaries: ids to containers and models to containers.
    """
    ids2containers = dict()
    models2containers = dict()

    for model_class, process_admin in models2admins.items():
        from generic_app.generic_models.html_report import HTMLReport
        if not issubclass(model_class, HTMLReport):

            if model_class._meta.abstract:
                raise ValueError(
                    'The model %s is abstract, but only concrete models can be registered' % model_class._meta.model_name)
        model_container = ModelContainer(model_class, process_admin, models2containers)
        ids2containers[model_container.id] = model_container

    return ids2containers, models2containers


def check_model_structure(model_sub_structure, registered_models_set):
    """
    Check the structure of the model sub-structure.

    Parameters
    ----------
    model_sub_structure : dict
        The model sub-structure to check.
    registered_models_set : set
        A set of registered model names.

    Raises
    ------
    ValueError
        If the structure is invalid.
    """
    for node, sub_tree in model_sub_structure.items():
        if isinstance(sub_tree, dict):
            check_model_structure(sub_tree, registered_models_set)
        else:
            if sub_tree is not None:
                raise ValueError('The leaves have to be None, but found %s' % type(sub_tree))
            if node not in registered_models_set:
                raise ValueError('There is no registered model with name %s' % node)


def get_readable_name_for(node_name, model_collection):
    """
    Get the readable name for a node.

    Parameters
    ----------
    node_name : str
        The name of the node.
    model_collection : ModelCollection
        The model collection to get the name from.

    Returns
    -------
    str
        The readable name for the node.
    """
    if node_name in model_collection.model_styling:
        return model_collection.model_styling[node_name]['name']
    elif node_name in model_collection.all_model_ids:
        model_container = model_collection.get_container(node_name)
        return model_container.title
    else:
        return node_name

READABLE_NAME = 'readable_name'
TYPE = 'type'

def enrich_model_structure_with_readable_names_and_types(node_name, model_tree, model_collection):
    """
    Enrich the model structure with readable names and types.

    Parameters
    ----------
    node_name : str
        The name of the node.
    model_tree : dict
        The model tree to enrich.
    model_collection : ModelCollection
        The model collection to use for enrichment.

    Returns
    -------
    dict
        The enriched model structure.
    """
    readable_name = get_readable_name_for(node_name, model_collection)
    if not model_tree:
        type = "Model"
        if HTMLReport in model_collection.get_container(node_name).model_class.__bases__:
            type = "HTMLReport"
        elif Process in model_collection.get_container(node_name).model_class.__bases__:
            type = "Process"
        return {READABLE_NAME: readable_name, TYPE: type}
    else:
        return {READABLE_NAME: readable_name, TYPE: "Folder", 'children': {
            subNodeName: enrich_model_structure_with_readable_names_and_types(subNodeName, subTree, model_collection) for
            subNodeName, subTree in model_tree.items()}}


class ModelCollection:
    """
    Collection of models with additional metadata and functionality.

    Parameters
    ----------
    models2admins : dict
        A dictionary mapping models to their admin objects.
    model_structure : dict
        The structure of the models.
    model_styling : dict
        The styling information for the models.
    global_filters : dict
        The global filters for the models.

    Attributes
    ----------
    _ids2containers : dict
        A dictionary mapping IDs to containers.
    _models2containers : dict
        A dictionary mapping models to containers.
    model_structure : dict
        The structure of the models.
    model_styling : dict
        The styling information for the models.
    global_filters : dict
        The global filters for the models.
    model_structure_with_readable_names : dict
        The model structure enriched with readable names and types.
    """
    def __init__(self, models2admins, model_structure, model_styling, global_filters) -> None:
        super().__init__()

        ids2containers, models2containers = create_model_containers(models2admins)
        self._ids2containers = ids2containers
        self._models2containers = models2containers

        for c in self.all_containers:
            c.read_dependencies()

        if model_structure:
            check_model_structure(model_structure, self.all_model_ids)
        else:
            model_structure = {'Models': {c.id: None for c in self.all_containers}}
        self.model_structure = model_structure
        self.model_styling = model_styling
        self.global_filters = global_filters

        self.model_structure_with_readable_names = {
            node_name: enrich_model_structure_with_readable_names_and_types(node_name, sub_tree, self) for node_name, sub_tree in
            self.model_structure.items()}

    @property
    def all_containers(self):
        """
        Get all model containers.

        Returns
        -------
        dict_values
            All model containers.
        """
        return self._ids2containers.values()

    @property
    def all_model_ids(self):
        """
        Get all model IDs.

        Returns
        -------
        set
            A set of all model IDs.
        """
        return set([c.id for c in self.all_containers])

    def get_container(self, id_or_model_class):
        """
        Get the container for a given ID or model class.

        Parameters
        ----------
        id_or_model_class : str or type
            The ID or model class to get the container for.

        Returns
        -------
        ModelContainer
            The container for the given ID or model class.

        Raises
        ------
        ValueError
            If the given item is not a string or a model.
        """
        if isinstance(id_or_model_class, str):
            return self._ids2containers[id_or_model_class]
        elif issubclass(id_or_model_class, Model):
            return self._models2containers[id_or_model_class]
        else:
            raise ValueError(
                f'The given item has to be a string or a model, but found {id_or_model_class} with type {type(id_or_model_class)}')
