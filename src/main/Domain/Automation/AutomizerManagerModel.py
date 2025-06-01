

import asyncio, threading, queue, time
from queue import Full
from ..User.UserManagerModel import UserManager
from fastapi.responses import JSONResponse
from Infrastructure.Logging import write_log
class Automizer_Manager:
    _instance = None
    _lock = threading.Lock() #Prevent race condition for create the first instance of class
    def __new__(cls, *args, **kwargs): #singleton pattern
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Automizer_Manager, cls).__new__(cls)
                    # Initialize attributes ONCE during creation
                    cls._instance.userManager = UserManager()
                    cls._instance.request_queue = queue.Queue()
                    cls._instance.tasks = set()
                    cls._instance.automizerList = []
                    cls._instance.loop = None
                    cls._instance.request_process_thread = None
                    cls._instance.start()
        return cls._instance

    def start(self):
        #start a thread for the manager
        if not self.request_process_thread or not self.request_process_thread.is_alive():
            self.request_process_thread = threading.Thread(target=self.run_loop, daemon=True)
            self.request_process_thread.start()

    def run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.process_requests())
        for user in self.userManager.store.values():
            self.loop.create_task(user.automizer.EnforceRule())
        self.loop.run_forever()

    async def process_requests(self):
        while True:
            RuleDescription = await self.loop.run_in_executor(None, self.request_queue.get)
            if RuleDescription == "STOP":
                break
            await self.handle_request(RuleDescription)


    async def handle_request(self, RuleDescription: dict):
        user = self.userManager.get(RuleDescription["Header"]["User"])
        if not user:
            write_log(f"user {RuleDescription['Header']['User']} not found.")
            return

        #in case user just added to the system
        if not user.automizer.running:
            self.loop.create_task(user.automizer.EnforceRule())

        if RuleDescription["Header"]["OperationType"] == "ADD":
            task = asyncio.create_task(user.automizer.AddRule(RuleDescription))
        else:
            task = asyncio.create_task(user.automizer.UpdateRuleSet(RuleDescription))

        self.tasks.add(task)
        task.add_done_callback(lambda t: self.tasks.remove(t))

    def submit_request(self, RuleDescription: dict):
        try:
            self.request_queue.put(RuleDescription, timeout=2)
            return JSONResponse(
                status_code=201,
                content={"message": "Automation Rule request submitted"}
            )
        except Full:
            return JSONResponse(
                status_code=503,
                content={"error": "Automation Rule queue is full"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Automation Rule request cannot be submitted: {e}"}
            )

    def stop(self):
        write_log("Shutting down automation manager...")
        # Trigger `process_requests()` to break
        self.request_queue.put("STOP")

        for user in self.userManager.store.values():
            self.loop.create_task(user.automizer.StopEnforcing())

        if not self.loop or not self.tasks:
            return

        async def wait_all():
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)

        future = asyncio.run_coroutine_threadsafe(wait_all(), self.loop)

        # Block the current thread until tasks complete or timeout
        future.result(timeout=timeout)  # Will raise concurrent.futures.TimeoutError if timeout exceeded

        # shutdown the event loop thread
        if self.loop and self.loop.is_running():
            self.loop.stop()

        # Wait for thread to finish
        if self.request_process_thread and self.request_process_thread.is_alive():
            self.request_process_thread.join()

        # clear the task set
        self.tasks.clear()




