from typing import Iterable

IsCanceled = bool
Canceled = True
NotCanceled = False


class event:
    def __init__(self, cancelable=False):
        self.subscribers = set()
        self._cancelable = cancelable

    @property
    def cancelable(self) -> bool:
        return self._cancelable

    def __call__(self, sender, *args, **kwargs) -> IsCanceled:
        """
        Raise the event
        :param sender: first para must be the sender
        :return: whether the event was canceled
        """
        return self.invoke(sender, *args, **kwargs)

    def add(self, *args) -> "event":
        for subscriber in args:
            self.subscribers.add(subscriber)
        return self

    def remove(self, subscriber) -> "event":
        self.subscribers.remove(subscriber)
        return self

    def clear(self) -> "event":
        self.subscribers.clear()
        return self

    def invoke(self, sender, *args, **kwargs) -> IsCanceled:
        """
        Raise the event
        :param sender: first para must be the sender
        :return: whether the event was canceled
        """
        if self.cancelable:
            for subscriber in self.subscribers:
                canceled = subscriber(sender, *args, **kwargs)
                if canceled:
                    return Canceled
        else:
            for subscriber in self.subscribers:
                subscriber(sender, *args, **kwargs)
        return NotCanceled

    def __iadd__(self, other):
        if isinstance(other, Iterable):
            self.add(*other)
        else:
            self.add(other)
