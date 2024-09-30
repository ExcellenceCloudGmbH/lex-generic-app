import os

from generic_app.rest_api.calculated_model_updates.update_handler import CalculatedModelUpdateHandler
from django.dispatch import receiver

from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save)
def calculation_ids(sender, instance, created, **kwargs):
    """
    Handles the post_save signal for CalculationIDs model.

    Sends a message to the 'calculations' channel group with the calculation ID details.

    Parameters
    ----------
    sender : Model
        The model class that sent the signal.
    instance : Model instance
        The actual instance being saved.
    created : bool
        A boolean indicating whether a new record was created.
    **kwargs : dict
        Additional keyword arguments.
    """
    from generic_app.submodels.CalculationIDs import CalculationIDs

    if sender == CalculationIDs:
        channel_layer = get_channel_layer()

        calculation_record = instance.calculation_record
        calculation_id = instance.calculation_id
        context_id = instance.context_id

        message = {
            'type': 'calculation_id',
            'payload': {
                'calculation_record': calculation_record,
                'calculation_id': calculation_id,
                'context_id': context_id
            }
        }
        async_to_sync(channel_layer.group_send)("calculations", message)
@receiver(post_save)
def calculation_logs(sender, instance, created, **kwargs):
    """
    Handles the post_save signal for CalculationLog and UserChangeLog models.

    Sends a real-time log message to the channel group associated with the calculation record.

    Parameters
    ----------
    sender : Model
        The model class that sent the signal.
    instance : Model instance
        The actual instance being saved.
    created : bool
        A boolean indicating whether a new record was created.
    **kwargs : dict
        Additional keyword arguments.
    """
    from generic_app.submodels.CalculationLog import CalculationLog
    from generic_app.submodels.UserChangeLog import UserChangeLog

    if created and (sender == CalculationLog or sender == UserChangeLog):
        channel_layer = get_channel_layer()
        message = {
            'type': 'calculation_log_real_time', # This is the correct naming convention
            'payload': get_model_data(instance.calculation_record, instance.calculationId)
        }
        async_to_sync(channel_layer.group_send)(f'{instance.calculation_record}', message)
@receiver(post_save)
def send_calculation_notification(sender, instance, created, **kwargs):
    """
    Handles the post_save signal for CalculationLog model to send notifications.

    Sends a notification message to the 'calculation_notification' channel group if the instance has notifications enabled.

    Parameters
    ----------
    sender : Model
        The model class that sent the signal.
    instance : Model instance
        The actual instance being saved.
    created : bool
        A boolean indicating whether a new record was created.
    **kwargs : dict
        Additional keyword arguments.
    """
    from generic_app.submodels.CalculationLog import CalculationLog

    if created and sender == CalculationLog and instance.is_notification:
        channel_layer = get_channel_layer()
        message = {
            'type': 'calculation_notification', # This is the correct naming convention
            'payload': {
                'id': instance.id,
                'message': instance.message,
            }
        }
        # notification = Notifications(message=instance.message, timestamp=datetime.now())
        # notification.save()
        async_to_sync(channel_layer.group_send)(f'calculation_notification', message)

def update_calculation_status(instance):
    """
    Updates the calculation status for instances of ConditionalUpdateMixin.

    Sends a message to the 'update_calculation_status' channel group indicating that the calculation is completed.

    Parameters
    ----------
    instance : Model instance
        The instance whose status is being updated.
    """
    from generic_app.generic_models.upload_model import ConditionalUpdateMixin

    if issubclass(instance.__class__, ConditionalUpdateMixin):
        channel_layer = get_channel_layer()
        message = {
            'type': 'calculation_is_completed', # This is the correct naming convention
            'payload': {
                'record': str(instance),
                'record_id': f"{instance._meta.model_name}_{instance.id}"
            }
        }
        # notification = Notifications(message="Calculation is finished", timestamp=datetime.now())
        # notification.save()
        async_to_sync(channel_layer.group_send)(f'update_calculation_status', message)

def get_model_data(calculation_record, calculationId):
    """
    Retrieves log messages for a given calculation record and ID.

    Fetches messages from UserChangeLog and CalculationLog models and combines them into a single string.

    Parameters
    ----------
    calculation_record : str
        The calculation record identifier.
    calculationId : int
        The calculation ID.

    Returns
    -------
    str
        Combined log messages from UserChangeLog and CalculationLog.
    """
    from generic_app.submodels.CalculationLog import CalculationLog
    from generic_app.submodels.UserChangeLog import UserChangeLog

    messages = []

    # Fetch messages from UserChangeLog
    queryset_ucl = UserChangeLog.objects.filter(calculation_record=calculation_record,
                                                calculationId=calculationId).only('timestamp', 'message')
    messages.extend(f"{message.timestamp} {message.message}" for message in queryset_ucl)

    # Fetch messages from CalculationLog
    queryset_calc = CalculationLog.objects.filter(calculation_record=calculation_record,
                                                  calculationId=calculationId).only('timestamp', 'message')
    messages.extend(f"{message.timestamp} {message.message}" for message in queryset_calc)

    return "\n".join(messages)

def do_post_save(sender, **kwargs):
    """
    Handles custom post-save actions.

    Registers the save event with the CalculatedModelUpdateHandler.

    Parameters
    ----------
    sender : Model
        The model class that sent the signal.
    **kwargs : dict
        Additional keyword arguments.
    """
    CalculatedModelUpdateHandler.register_save(kwargs['instance'])

from django.dispatch import Signal

custom_post_save = Signal()

