from django.db.models import TextField


class HTMLField(TextField):
    """
    A custom Django model field for storing HTML content.

    This field inherits from Django's TextField and sets a default
    maximum length for the HTML content.

    Attributes
    ----------
    max_length : int
        The maximum length of the HTML content. Default is 1000 characters.
    """
    max_length = 1000
    pass