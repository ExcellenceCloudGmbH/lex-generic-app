from generic_app.rest_api.models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from generic_app import generic_models


class UserChangeLog(generic_models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = generic_models.AutoField(primary_key=True)
    user_name = generic_models.TextField()
    timestamp = generic_models.DateTimeField()
    message = generic_models.TextField()
    traceback = generic_models.TextField(default="", null=True)
    calculationId = generic_models.TextField(default='-1')

    def save(self, *args, **kwargs):
        if self.id is None:
            super(UserChangeLog, self).save(*args, **kwargs)