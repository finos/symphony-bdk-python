from abc import ABC, abstractmethod

# Abstract class for IM listener
# class is just an interface of functions to handle the Elements Actions events received
# from DataFeed
# (see Real Time Events in REST API documentation for more details)
# the developer will handle actual event logic in your implementation of
# this abstract class


class ElementsActionListener(ABC):

    @abstractmethod
    def on_elements_action(self, action):
        """
        Do Something
        """
