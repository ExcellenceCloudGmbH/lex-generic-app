import contextvars
from uuid import uuid4

# Define a context variable
context_id = contextvars.ContextVar('context_id', default=None)

# Context manager to set operation id
class OperationContext:
    """
    Context manager to set and manage an operation ID using context variables.

    This context manager ensures that an operation ID is set for the duration
    of the context. If an operation ID is not already set, it generates a new
    one using UUID.

    Methods
    -------
    __enter__()
        Sets a new operation ID if one doesn't already exist and returns it.
    __exit__(exc_type, exc_val, exc_tb)
        Optionally resets or clears the operation ID.
    """
    def __enter__(self):
        """
        Enter the runtime context related to this object.

        This method sets a new operation ID if one doesn't already exist.

        Returns
        -------
        str
            The current operation ID.
        """
        # Set a new operation id if one doesn't already exist
        if context_id.get() is None:
            context_id.set(str(uuid4()))
        return context_id.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.

        This method can optionally reset or clear the operation ID.

        Parameters
        ----------
        exc_type : type
            The exception type.
        exc_val : Exception
            The exception instance.
        exc_tb : traceback
            The traceback object.
        """
        # Optionally, reset or clear the operation id here if necessary
        pass