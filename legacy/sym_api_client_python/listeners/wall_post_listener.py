from abc import ABC, abstractmethod

# Abstract class for wallpost listener
# class is just an interface of functions to handle the connection events
# received from DataFeed Connection Events are "SHAREDPOST" and
# "MESSAGESENT" handle actual event logic in your implementation of
# this abstract class


class WallPostListener(ABC):

    @abstractmethod
    def on_wall_post_msg(self, user):
        pass

    @abstractmethod
    def on_shared_post(self, user):
        pass
