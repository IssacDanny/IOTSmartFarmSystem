import threading, queue
class FairLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._wait_queue = queue.Queue()
        self._owner = None

    def acquire(self):
        event = threading.Event()
        self._wait_queue.put(event)

        while True:
            if self._wait_queue.queue[0] is event:
                with self._lock:
                    self._owner = threading.get_ident()
                    break
            event.wait()

    def release(self):
        with self._lock:
            if self._owner != threading.get_ident():
                raise RuntimeError("Only lock owner can release")
            self._wait_queue.get()
            self._owner = None
            if not self._wait_queue.empty():
                self._wait_queue.queue[0].set()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
