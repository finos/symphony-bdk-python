from abc import ABC, abstractmethod

#Abstract class for connections listener
#class is just an interface of functions to handle the connection events recieved from DataFeed
#Connection Events are "CONNECTIONREQUESTED" and "CONNECTIONACCEPTED"
#handle actual event logic in your implementation of this abstract class
class ConnectionListener(ABC):

    @abstractmethod
    def onConnectionAccepted(self, user):
        """
        Do Something
        """

    @abstractmethod
    def onConnectionRequested(self, user):
        """
        Do Something
        """
