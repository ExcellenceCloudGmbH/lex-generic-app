from generic_app.generic_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from generic_app import models


class UserChangeLog(models.Model):
    """
    A model to log changes made by users.

    Attributes
    ----------
    modification_restriction : AdminReportsModificationRestriction
        Restriction applied to modifications.
    id : AutoField
        Primary key for the log entry.
    user_name : TextField
        Name of the user who made the change.
    timestamp : DateTimeField
        Time when the change was made.
    message : TextField
        Message describing the change.
    traceback : TextField, optional
        Traceback information if available (default is an empty string).
    calculationId : TextField, optional
        ID of the calculation associated with the change (default is '-1').
    calculation_record : TextField, optional
        Record of the calculation (default is 'legacy').
    """
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    user_name = models.TextField()
    timestamp = models.DateTimeField()
    message = models.TextField()
    traceback = models.TextField(default="", null=True)
    calculationId = models.TextField(default='-1')
    calculation_record = models.TextField(default="legacy")

    def save(self, *args, **kwargs):
        """
        Save the current instance.

        If the instance is new (id is None), it calls the parent class's save method.

        Parameters
        ----------
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.
        """
        if self.id is None:
            super(UserChangeLog, self).save(*args, **kwargs)