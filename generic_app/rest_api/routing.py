from django.urls import path

from generic_app.rest_api.consumers.CalculationNotificationConsumer import CalculationNotificationConsumer
from generic_app.rest_api.consumers.BackendHealthConsumer import BackendHealthConsumer
from generic_app.rest_api.consumers.CalculationLogConsumer import CalculationLogConsumer
from generic_app.rest_api.consumers.MonitoringConsumer import MonitoringConsumer
from generic_app.rest_api.consumers.NotificationsConsumer import NotificationsConsumer
from generic_app.rest_api.consumers.UpdateCalculationStatusConsumer import UpdateCalculationStatusConsumer

websocket_urlpatterns = [
    path('ws/health', BackendHealthConsumer.as_asgi(),
                 name='backend-health'),
    path('ws/monitoring', MonitoringConsumer.as_asgi(),
         name='monitoring'),
    path('ws/notifications/<str:host>', NotificationsConsumer.as_asgi(),
         name='notifications'),
    path('ws/calculation_logs/<str:calculationId>', CalculationLogConsumer.as_asgi(),
         name='calculation-logs'),
    path('ws/calculation_notifications/<str:host>', CalculationNotificationConsumer.as_asgi(),
         name='calculation-notifications'),
    path('ws/calculation_status_update/<str:host>', UpdateCalculationStatusConsumer.as_asgi(),
         name='calculation-status-update'),

]
