from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.http import HttpResponse
from django.urls import path, register_converter
from rest_framework_simplejwt.views import TokenRefreshView

from generic_app.rest_api.auth import TokenObtainPairWithUserView
from generic_app.rest_api.model_collection.model_collection import ModelCollection
from generic_app.generic_models.calculated_model import CalculatedModelMixin
from generic_app.generic_models.model_process_admin import ModelProcessAdmin
from generic_app.rest_api.views.calculations.CleanCalculations import CleanCalculations
from generic_app.rest_api.views.file_operations.FileDownload import FileDownloadView
from generic_app.rest_api.views.file_operations.ModelExport import ModelExportView
from generic_app.rest_api.views.sharepoint.SharePointFileDownload import SharePointFileDownload
from generic_app.rest_api.views.sharepoint.SharePointPreview import SharePointPreview
from generic_app.rest_api.views.sharepoint.SharePointShareLink import SharePointShareLink
from generic_app.rest_api.signals import do_post_save

from generic_app.rest_api.views.model_info.Fields import Fields
from generic_app.rest_api.views.model_info.Widgets import Widgets
from generic_app.rest_api.views.model_relation_views import ModelStructureObtainView, Overview, ProcessStructure
from generic_app.rest_api.views.model_entries.List import ListModelEntries
from generic_app.rest_api.views.model_entries.Many import ManyModelEntries
from generic_app.rest_api.views.model_entries.One import OneModelEntry
from generic_app.rest_api.views.permissions.ModelPermissions import ModelPermissions
from generic_app.rest_api.views.process_flow.CreateOrUpdate import CreateOrUpdate
from generic_app.rest_api.views.project_info.ProjectInfo import ProjectInfo
from generic_app.rest_api.views.calculations.InitCalculationLogs import InitCalculationLogs

from generic_app.rest_api import converters
from generic_app.rest_api.views.global_search_for_models.Search import Search

class ProcessAdminSite:
    """
    Used as instance, i.e. inheriting this class is not necessary in order to use it.
    """
    name = 'process_admin_rest_api'

    def __init__(self) -> None:
        """
        Initialize the ProcessAdminSite with default attributes.
        """
        super().__init__()

        self.registered_models = {}  # Model-classes to ModelProcessAdmin-instances
        self.model_structure = {}
        self.model_styling = {}
        self.global_filter = {}
        self.global_filter_structure = {}
        self.html_reports = {}
        self.processes = {}

        self.initialized = False
        self.model_collection = None
    def register_model_styling(self, model_styling):
        """
        Register model styling parameters.

        Parameters
        ----------
        model_styling : dict
            Dictionary that contains styling parameters for each model.
        """
        self.model_styling = model_styling

    def register_global_filter_structure(self, global_filter_structure):
        """
        Register global filter structure.

        Parameters
        ----------
        global_filter_structure : dict
            Dictionary that contains information on which models are affected by the global filtering.
        """
        self.global_filter_structure = global_filter_structure

    def registerHTMLReport(self, name, report):
        """
        Register an HTML report.

        Parameters
        ----------
        name : str
            The name of the report.
        report : object
            The report object to be registered.
        """
        self.html_reports[name] = report

    def registerProcess(self, name, process):
        """
        Register a process.

        Parameters
        ----------
        name : str
            The name of the process.
        process : object
            The process object to be registered.
        """
        self.processes[name] = process

    def register_model_structure(self, model_structure):
        """
        Register model structure.

        Parameters
        ----------
        model_structure : dict
            Multiple trees that structure the registered models. The leaves of the trees must correspond to the model-names,
            and all other nodes are interpreted as model categories. The roots have a special meaning, i.e., their categorization
            should be the most general one and is represented in a special way.

            Example
            -------
            {
                'Main_1': {
                    'Sub_1_1': {
                        'Model_1_1_1': None,
                        'Model_1_1_2': None
                    }
                },
                'Main2': {
                    'Sub_2_1': {
                        'Model_2_1_1': None,
                        'Model_2_1_2': None
                    },
                    'Sub_2_2': {
                        'Model_2_2_1': None,
                        'Model_2_2_2': None
                    }
                }
            }

            Note: Not every model has to be contained in this tree.
        """
        self.model_structure = model_structure

    def register(self, model_or_iterable, process_admin=None):
        """
        Register a model or iterable of models with an optional process admin.

        Parameters
        ----------
        model_or_iterable : ModelBase or iterable
            The model or iterable of models to be registered.
        process_admin : ModelProcessAdmin, optional
            The process admin instance to be associated with the model(s). If not provided, a new instance of ModelProcessAdmin is created.
        """
        if process_admin is None:
            process_admin = ModelProcessAdmin()

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]

        for model in model_or_iterable:
            if model in self.registered_models:
                raise Exception('Model %s already registered' % model._meta.model_name)
            else:
                self.registered_models[model] = process_admin
                # TODO why was this in here in the first place?
                # if not issubclass(model, CalculatedModelMixin):
                post_save.connect(do_post_save, sender=model)

    def create_model_objects(self, request):
        """
        Create model objects for registered models that are subclasses of CalculatedModelMixin.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        HttpResponse
            HTTP response indicating the creation status.
        """
        for model in self.registered_models:
            if issubclass(model, CalculatedModelMixin):
                model.create()
        return HttpResponse("Created")

    def _get_urls(self):
        """
        Get the URL patterns for the registered models and views.

        Returns
        -------
        list
            List of URL patterns.
        """
        register_converter(converters.create_model_converter(self.model_collection), 'model')

        urlpatterns = [
            path('api/model-structure', ModelStructureObtainView.as_view(model_collection=self.model_collection),
                 name='model-structure'),
            path('api/auth/token/', TokenObtainPairWithUserView.as_view(), name='token'),
            path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
            path('api/<model:model_container>/file-download',
                 FileDownloadView.as_view(model_collection=self.model_collection), name='file-download'),
            path('api/<model:model_container>/export',
                 ModelExportView.as_view(model_collection=self.model_collection), name='model-export'),
            path('api/htmlreport/<str:report_name>',
                 Overview.as_view(HTML_reports=self.html_reports), name='htmlreports'),
            path('api/process/<str:process_name>',
                 ProcessStructure.as_view(processes=self.processes), name='process'),
        ]

        url_patterns_for_react_admin = [
            path('api/model_entries/<model:model_container>/list', ListModelEntries.as_view(),
                 name='model-entries-list'),
            path('api/model_entries/<model:model_container>/<str:calculationId>/one/<int:pk>', OneModelEntry.as_view(),
                 name='model-one-entry-read-update-delete'),
            path('api/model_entries/<model:model_container>/<str:calculationId>/one', OneModelEntry.as_view(), name='model-one-entry-create'),
            path('api/run_step/<model:model_container>/<str:pk>', CreateOrUpdate.as_view(),
                 name='run_step'),
            path('api/model_entries/<model:model_container>/many', ManyModelEntries.as_view(),
                 name='model-many-entries'),
            path('api/global-search/<str:query>', Search.as_view(model_collection=self.model_collection),
                 name='global-search'),
            path('api/<model:model_container>/model-permissions', ModelPermissions.as_view(), name='model-restrictions'),
            path('api/project-info', ProjectInfo.as_view(),
                 name='project-info'),
            path('api/widget_structure', Widgets.as_view(), name='widget-structure'),
            path('api/init-calculation-logs', InitCalculationLogs.as_view(),
                 name='init-calculation-logs'),
            path('api/clean-calculations', CleanCalculations.as_view(),
                 name='clean-calculations'),
        ]

        url_patterns_for_model_info = [
            path('api/model_info/<model:model_container>/fields', Fields.as_view(), name='model-info-fields'),
        ]

        url_patterns_for_sharepoint = [
            path('api/<model:model_container>/sharepoint-file-download', SharePointFileDownload.as_view(), name='sharepoint-file-download'),
            path('api/<model:model_container>/sharepoint-file-share-link', SharePointShareLink.as_view(),
                 name='sharepoint-file-share-link'),
            path('api/<model:model_container>/sharepoint-file-preview-link', SharePointPreview.as_view(),
                 name='sharepoint-file-preview-link'),
        ]

        return urlpatterns + url_patterns_for_react_admin + url_patterns_for_model_info + url_patterns_for_sharepoint

    @property
    def urls(self):
        """
        Get the URLs for the process admin site.

        Returns
        -------
        tuple
            A tuple containing the URL patterns, the app name, and the instance name.
        """
        # TODO: Move this to a logically more appropriate place
        # TODO: remove tree induction
        if not self.initialized:
            self.model_collection = ModelCollection(self.registered_models, self.model_structure,
                                                    self.model_styling, self.global_filter_structure)
            self.initialized = True

        return self._get_urls(), 'process_admin', self.name  # TODO: what is the name exactly for??
