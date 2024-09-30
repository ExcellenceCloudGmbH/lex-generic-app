import os
import threading
import traceback
from datetime import datetime

from celery import current_task

from generic_app.generic_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from generic_app.rest_api.context import context_id
from generic_app import models
import inspect
from django.core.cache import cache
from lex.lex_app import settings

from generic_app.submodels.CalculationIDs import CalculationIDs

#### Note: Messages shall be delivered in the following format: "Severity: Message" The colon and the whitespace after are required for the code to work correctly ####
# Severity could be something like 'Error', 'Warning', 'Caution', etc. (See Static variables below!)


class CalculationLog(models.Model):
    """
    A model to log calculation events with various severities and message types.

    Attributes
    ----------
    modification_restriction : AdminReportsModificationRestriction
        Restriction for modification.
    id : AutoField
        Primary key for the log entry.
    timestamp : DateTimeField
        Timestamp of the log entry.
    trigger_name : TextField, optional
        Name of the trigger that caused the log entry.
    message_type : TextField
        Type of the message.
    calculationId : TextField
        ID of the calculation.
    calculation_record : TextField
        Record of the calculation.
    message : TextField
        The log message.
    method : TextField
        Method that generated the log.
    is_notification : BooleanField
        Flag to indicate if the log is a notification.

    Class Attributes
    ----------------
    SUCCESS : str
        Success severity prefix.
    WARNING : str
        Warning severity prefix.
    ERROR : str
        Error severity prefix.
    START : str
        Start severity prefix.
    FINISH : str
        Finish severity prefix.
    PROGRESS : str
        Progress message type.
    INPUT : str
        Input validation message type.
    OUTPUT : str
        Output validation message type.
    """
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    trigger_name = models.TextField(null=True)
    message_type = models.TextField(default="")
    calculationId = models.TextField(default='test_id')
    calculation_record = models.TextField(default="legacy")
    message = models.TextField()
    method = models.TextField()
    is_notification = models.BooleanField(default=False)

    # Severities, to be concatenated with message in create statement
    SUCCESS = 'Success: '
    WARNING = 'Warning: '
    ERROR = 'Error: '
    START = 'Start: '
    FINISH = 'Finish: '

    # Message types
    PROGRESS = 'Progress'
    INPUT = 'Input Validation'
    OUTPUT = 'Output Validation'

    def save(self, *args, **kwargs):
        """
        Save the log entry to the database.

        Parameters
        ----------
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.
        """
        print(self.calculationId + ": " + self.message)
        if self.id is None:
            super(CalculationLog, self).save(*args, **kwargs)

    @classmethod
    def create(cls, message, message_type="Progress", trigger_name=None, is_notification=False):
        """
        Create a new log entry.

        Parameters
        ----------
        message : str
            The log message.
        message_type : str, optional
            Type of the message (default is "Progress").
        trigger_name : str, optional
            Name of the trigger that caused the log entry.
        is_notification : bool, optional
            Flag to indicate if the log is a notification (default is False).
        """
        trace_objects = cls.get_trace_objects()["trace_objects"]
        calculation_record = cls.get_trace_objects()["first_model_info"]

        if current_task and os.getenv("CELERY_ACTIVE"):
            obj, created = CalculationIDs.objects.get_or_create(calculation_record=calculation_record if calculation_record else "init_upload",
                                                                calculation_id=str(current_task.request.id),
                                                                defaults={
                                                                    'context_id': getattr(CalculationIDs.objects.filter(calculation_id=str(current_task.request.id)).first(), "context_id", "test_id")})
            calculation_id = getattr(obj, "calculation_id", "test_id")
        else:
            obj, created = CalculationIDs.objects.get_or_create(calculation_record=calculation_record if calculation_record else "init_upload",
                                                                context_id=context_id.get() if context_id.get() else "test_id",
                                                                defaults={
                                                                    'calculation_id': getattr(CalculationIDs.objects.filter(context_id=context_id.get()).first(), "calculation_id", "test_id")})
            calculation_id = getattr(obj, "calculation_id", "test_id")

        calc_log = CalculationLog(timestamp=datetime.now(), method=str(trace_objects),
                                  calculation_record=calculation_record if calculation_record else "init_upload", message=message, calculationId=calculation_id,
                                  message_type=message_type,
                                  trigger_name=trigger_name, is_notification=is_notification)
        calc_log.save()

    @classmethod
    def get_calculation_id(cls, calculation_model):
        """
        Get the calculation ID from the calculation model.

        Parameters
        ----------
        calculation_model : Model
            The calculation model instance.

        Returns
        -------
        str
            The calculation ID.
        """
        return f"{str(calculation_model._meta.model_name)}-{str(calculation_model.id)}" if calculation_model is not None else "test_id"

    @classmethod
    def get_trace_objects(cls):
        """
        Get the trace objects from the current stack.

        Returns
        -------
        dict
            A dictionary containing trace objects, first model info, and trace objects class list.
        """
        stack = list(traceback.extract_stack())
        currentframe = inspect.currentframe()
        trace_objects = []
        trace_objects_class_list = []
        first_model_info = None
        i = 0
        while currentframe is not None:
            if 'self' in currentframe.f_locals:
                tempobject = currentframe.f_locals['self']
            else:
                tempobject = None
            filename, methodname, lineno = stack[-(i + 1)].filename, stack[-(i + 1)].name, stack[-(i + 1)].lineno
            i += 1
            currentframe = currentframe.f_back
            if f"{settings.repo_name}" in filename and not "CalculationLog" in filename:
                trimmed_filename = filename.split(os.sep)[-1].split(".")[0]
                if tempobject and hasattr(tempobject, "_meta") and not first_model_info:
                    model_verbose_name = tempobject._meta.model_name
                    record_id = getattr(tempobject, 'id', None)
                    if model_verbose_name and record_id:
                        first_model_info = f"{model_verbose_name}_{record_id}"
                trace_objects.append((trimmed_filename, methodname, lineno, str(tempobject)))
                if hasattr(tempobject, "_meta"):
                    trace_objects_class_list.append(tempobject._meta.model_name)
        trace_objects.reverse()

        result = {
            "trace_objects": trace_objects,
            "first_model_info": first_model_info,
            "trace_objects_class_list": list(set(trace_objects_class_list))
        }

        return result

    @classmethod
    def assertTrue(cls, assertion, message):
        """
        Create a log entry based on the assertion result.

        Parameters
        ----------
        assertion : bool
            The assertion result.
        message : str
            The log message.
        """
        if assertion:
            cls.create(message=message, message_type="Test: Success")
        else:
            cls.create(message=message, message_type="Test: Error")
