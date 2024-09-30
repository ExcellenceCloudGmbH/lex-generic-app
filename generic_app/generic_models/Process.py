from django.db.models import Model


class Process(Model):
    """
    Abstract base class for processes.

    This class should be subclassed to create specific process models.
    It includes a method that must be implemented by subclasses to define
    the structure of the process.
    """

    class Meta():
        """
        Meta options for the Process model.

        This model is abstract and should not be used to create any database table.
        """
        abstract = True

    def get_structure(self):
        """
        Get the structure of the process.

        This method must be implemented by subclasses to define the specific
        structure of the process.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method")

