from asyncio.queues import Queue, QueueFull


class MessageAnnouncer:
    def __init__(self):
        self.listeners: list[Queue] = []

    def listen(self):
        self.listeners.append(Queue(maxsize=3))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except QueueFull:
                del self.listeners[i]


__all__ = ["MessageAnnouncer"]
