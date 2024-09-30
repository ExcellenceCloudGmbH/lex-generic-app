import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BackendHealthConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer to monitor backend health.

    This consumer handles WebSocket connections to check the health status
    of the backend. It maintains a set of active consumers and provides
    methods to connect, disconnect, and receive messages.

    Attributes
    ----------
    active_consumers : set
        A set to keep track of active consumers.
    """
    active_consumers = set()
    async def connect(self):
        """
        Handle a new WebSocket connection.

        This method accepts the WebSocket connection and adds the consumer
        to the set of active consumers.
        """
        await self.accept()
        self.active_consumers.add(self)
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.

        This method removes the consumer from the set of active consumers
        and calls the parent class's disconnect method.

        Parameters
        ----------
        close_code : int
            The WebSocket close code.
        """
        await super().disconnect(close_code)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.

        This method sends a JSON response indicating the health status of
        the backend.

        Parameters
        ----------
        text_data : str
            The incoming message data.
        """
        await self.send(text_data=json.dumps({
            'status': "Healthy :)"
        }))

    @classmethod
    async def disconnect_all(cls):
        """
        Disconnect all active consumers.

        This class method iterates over the set of active consumers and
        disconnects each one.
        """
        for consumer in cls.active_consumers.copy():
            await consumer.disconnect(None)
