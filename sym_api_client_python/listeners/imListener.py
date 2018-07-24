from abc import ABC, abstractmethod

#Abstract class for IM listener
#class is just an interface of functions to handle the IM events recieved from DataFeed
#(see Real Time Events in REST API documentation for more details)
#the developer will handle actual event logic in your implementation of this abstract class
class IMListener(ABC):

    @abstractmethod
    def onIMMessage(self, message):
        """
        Do Something
        """

    @abstractmethod
    def onIMCreated(self, stream):
        """
        Do Something
        """
