import asyncio, threading, queue, time
from queue import Full
from Infrastructure.Logging import write_log
from ..User.UserManagerModel import UserManager
from fastapi.responses import JSONResponse
class Controller_Manager:
    _instance = None
    _lock = threading.Lock() #Prevent race condition for create the first instance of class
    def __new__(cls, *args, **kwargs): #singleton pattern
        if not cls._instance:
            with cls._lock:
                cls._instance = super(Controller_Manager, cls).__new__(cls)
                # Initialize attributes ONCE during creation
                cls._instance.userManager = UserManager()
                cls._instance.request_queue = queue.Queue()
                cls._instance.tasks = set()
                cls._instance.loop = None
                cls._instance.request_process_thread = None
                cls._instance.ActGen = None
                cls._instance.start()
        return cls._instance

    def start(self):
        #start a thread for the manager
        if not self.request_process_thread or not self.request_process_thread.is_alive():
            self.request_process_thread = threading.Thread(target=self.run_loop, daemon=True)
            self.request_process_thread.start()

    def run_loop(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.create_task(self.process_requests())
            self.loop.run_forever()
        except Exception as e:
            write_log(f"Error in run_loop: {e}")

    async def process_requests(self):
        while True:
            ActivationDescription = await self.loop.run_in_executor(None, self.request_queue.get)
            if ActivationDescription == "STOP":
                break
            await self.handle_request(ActivationDescription)


    async def handle_request(self, ActivationDescription: dict):
        user = self.userManager.get(ActivationDescription["Header"]["User"])
        if not user:
            write_log(f"user {ActivationDescription['Header']['User']} not found.")
            return

        task = asyncio.create_task(user.deviceController.ActiveDevice(ActivationDescription))
        self.tasks.add(task)
        task.add_done_callback(lambda t: self.tasks.remove(t))


    def submit_request(self, ActivationDescription):
        try:
            self.request_queue.put(ActivationDescription, timeout=2)
            return JSONResponse(
                status_code=201,
                content={"message": "Activation request submitted"}
            )
        except Full:
            return JSONResponse(
                status_code=503,
                content={"error": "Activation queue is full"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Activation request cannot be submitted: {e}"}
            )

    def stop(self):
        write_log("Shutting down controller manager...")
        # Trigger `process_requests()` to break
        self.request_queue.put("STOP")

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





