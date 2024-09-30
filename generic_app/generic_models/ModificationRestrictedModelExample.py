from django.db.models import Model

from generic_app.generic_models.ModelModificationRestriction import ModelModificationRestriction


class AdminReportsModificationRestriction(ModelModificationRestriction):
    """
    Restriction class for admin reports modification.

    This class defines the permissions for reading, modifying, creating, and deleting
    admin reports.

    Methods
    -------
    can_read_in_general(user, violations)
        Checks if the user can read in general.
    can_modify_in_general(user, violations)
        Checks if the user can modify in general.
    can_create_in_general(user, violations)
        Checks if the user can create in general.
    can_delete_in_general(user, violations)
        Checks if the user can delete in general.
    can_be_read(instance, user, violations)
        Checks if the instance can be read by the user.
    can_be_modified(instance, user, violations)
        Checks if the instance can be modified by the user.
    can_be_created(instance, user, violations)
        Checks if the instance can be created by the user.
    can_be_deleted(instance, user, violations)
        Checks if the instance can be deleted by the user.
    """

    def can_read_in_general(self, user, violations):
        return True

    def can_modify_in_general(self, user, violations):
        return False

    def can_create_in_general(self, user, violations):
        return False

    def can_delete_in_general(self, user, violations):
        return False

    def can_be_read(self, instance, user, violations):
        return True

    def can_be_modified(self, instance, user, violations):
        return False

    def can_be_created(self, instance, user, violations):
        return False

    def can_be_deleted(self, instance, user, violations):
        return False


class ExampleModelModificationRestriction(ModelModificationRestriction):
    """
    Example restriction class for model modification.

    This class serves as an example of how to define permissions for reading, modifying,
    and creating instances of a model.

    Methods
    -------
    can_read_in_general(user, violations)
        Checks if the user can read in general.
    can_modify_in_general(user, violations)
        Checks if the user can modify in general.
    can_create_in_general(user, violations)
        Checks if the user can create in general.
    can_be_read(instance, user, violations)
        Checks if the instance can be read by the user.
    can_be_modified(instance, user, violations)
        Checks if the instance can be modified by the user.
    can_be_created(instance, user, violations)
        Checks if the instance can be created by the user.
    """

    def can_read_in_general(self, user, violations):
        pass

    def can_modify_in_general(self, user, violations):
        pass

    def can_create_in_general(self, user, violations):
        pass

    def can_be_read(self, instance, user, violations):
        pass

    def can_be_modified(self, instance, user, violations):
        pass

    def can_be_created(self, instance, user, violations):
        pass


class ModificationRestrictedModelExample(Model):
    """
    Example model with modification restrictions.

    This model demonstrates how to restrict modifications of instances using a
    modification restriction class.

    Attributes
    ----------
    modification_restriction : ExampleModelModificationRestriction
        The restriction class that defines the permissions for this model.
    """
    modification_restriction = ExampleModelModificationRestriction()
