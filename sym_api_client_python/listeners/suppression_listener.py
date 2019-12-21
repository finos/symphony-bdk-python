from abc import ABC, abstractmethod

# Abstract class for message supression listener
# class is just an interface of functions to handle the connection events
# received from DataFeed Connection Event is "CONNECTIONREQUESTED"
# handle actual event logic in your implementation of
# this abstract class


class SuppressionListener(ABC):

    @abstractmethod
    def on_message_suppression(self, suppressed_message):
        pass