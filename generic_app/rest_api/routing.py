from django.urls import path

from generic_app.rest_api.consumers.BackendHealthConsumer import BackendHealthConsumer
from generic_app.rest_api.consumers.CalculationLogConsumer import CalculationLogConsumer
from generic_app.rest_api.consumers.UpdateCalculationStatusConsumer import UpdateCalculationStatusConsumer
from generic_app.rest_api.consumers.CalculationsConsumer import CalculationsConsumer

websocket_urlpatterns = [
    path('ws/health', BackendHealthConsumer.as_asgi(),
                 name='backend-health'),
    path('ws/calculations', CalculationsConsumer.as_asgi(),
                 name='calculations'),
    path('ws/calculation_logs/<str:calculationId>', CalculationLogConsumer.as_asgi(),
         name='calculation-logs'),
    path('ws/calculation_status_update', UpdateCalculationStatusConsumer.as_asgi(),
         name='calculation-status-update'),

]
