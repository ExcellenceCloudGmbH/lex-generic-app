from generic_app.generic_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from generic_app import models


class CalculationIDs(models.Model):
    """
    A Django model representing calculation IDs with modification restrictions.

    Attributes
    ----------
    modification_restriction : AdminReportsModificationRestriction
        Restriction applied to modifications of this model.
    id : AutoField
        The primary key for the model.
    context_id : TextField
        The context identifier, default is 'test_id'.
    calculation_record : TextField
        The record of the calculation.
    calculation_id : TextField
        The calculation identifier, default is 'test_id'.
    """
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    context_id = models.TextField(default='test_id')
    calculation_record = models.TextField()
    calculation_id = models.TextField(default='test_id')