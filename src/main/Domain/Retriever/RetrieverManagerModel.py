import asyncio, threading, queue
from ..User.UserManagerModel import UserManager
from Infrastructure.Logging import write_log

class RetrieverManager:
    _instance = None
    _lock = threading.Lock()  # Prevent race condition for create the first instance of class

    def __new__(cls, *args, **kwargs):  # singleton pattern
        if not cls._instance:
            with cls._lock:
                cls._instance = super(RetrieverManager, cls).__new__(cls)
                # Initialize attributes ONCE during creation
                cls._instance.userManager = UserManager()
                cls._instance.tasks = set()
                cls._instance.loop = None
                cls._instance.request_process_thread = None
                #cls._instance.start()
        return cls._instance

    def start(self):
        # start a thread for the manager
        if not self.request_process_thread or not self.request_process_thread.is_alive():
            self.request_process_thread = threading.Thread(target=self.run_loop, daemon=True)
            self.request_process_thread.start()

    def run_loop(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            for user in self.userManager.store.values():
                self.loop.create_task(user.retriever.mqttManager.sensorDataProducer())
            self.loop.run_forever()
        except Exception as e:
            write_log(f"Error in run_loop: {e}")

    def stop(self):
        write_log("Shutting down retriever manager...")
        for user in self.userManager.store.values():
            self.loop.create_task(user.retriever.StopConsumeData())

        if not self.loop or not self.tasks:
            return

        async def wait_all():
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)

        future = asyncio.run_coroutine_threadsafe(wait_all(), self.loop)

        # Block the current thread until tasks complete or timeout
        future.result(timeout=timeout)  # Will raise concurrent.futures.TimeoutError if timeout exceeded

        # Schedule shutdown in the event loop thread
        if self.loop and self.loop.is_running():
            self.loop.stop()

        # Wait for thread to finish
        if self.request_process_thread and self.request_process_thread.is_alive():
            self.request_process_thread.join()

        # Optionally: clear the task set
        self.tasks.clear()

