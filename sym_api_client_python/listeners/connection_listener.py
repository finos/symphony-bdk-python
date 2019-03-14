from abc import ABC, abstractmethod

# Abstract class for connections listener
# class is just an interface of functions to handle the connection events
# received from DataFeed Connection Events are "CONNECTIONREQUESTED" and
# "CONNECTIONACCEPTED" handle actual event logic in your implementation of
# this abstract class


class ConnectionListener(ABC):

    @abstractmethod
    def on_connection_accepted(self, user):
        pass

    @abstractmethod
    def on_connection_requested(self, user):
        pass
