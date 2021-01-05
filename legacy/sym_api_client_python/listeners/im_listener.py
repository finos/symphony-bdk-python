from abc import ABC, abstractmethod

# Abstract class for IM listener
# class is just an interface of functions to handle the IM events received
# from DataFeed
# (see Real Time Events in REST API documentation for more details)
# the developer will handle actual event logic in your implementation of
# this abstract class


class IMListener(ABC):

    @abstractmethod
    def on_im_message(self, message):
        """
        Do Something
        """

    @abstractmethod
    def on_im_created(self, stream):
        """
        Do Something
        """
