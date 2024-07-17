from time import sleep
import Pyro5.api as api
import Pyro5.errors
from . import actions
import threading as th


class remote_controller():
    def __init__(self, print_callback: callable, state_callback: callable, host_adress="localhost") -> None:
        self.print_callback = print_callback
        self.host_adress = host_adress
        self.wait_for_idle = th.Event()
        self.watcher_running = False
        self.state_callback = state_callback
        self.state = actions.Action.idle
        self.is_connected = False
        self.pyro_thread = None
        self.next_action = None
        
    def start_pyro_loop(self):
        if self.pyro_thread is not None:
            self._print("Pyro loop already running", "DC", "yellow")
            return
        self._print("Starting pyro thread")
        self.pyro_thread = th.Thread(target=self._pyro_loop)
        self.pyro_thread.start()

    def _pyro_loop(self):
        self._print("Pyro thread attempting to connect...")
        self.try_to_connect()
        self._print("Starting pyro loop")
        while self.is_connected:
            if self.next_action is not None:
                response: str = self.controller.set_action(self.next_action)
                if response.startswith("Cannot"):
                    self._print(response, "DC", "yellow")
                else:
                    self._print(response)
                    self.next_action = None
                    self.wait_for_idle.clear()
            new_state = actions.Action(self.controller.get_current_action())
            if self.state != new_state:
                self._print(
                    f"State changed from {self.state} to {new_state}")
                self.state = new_state
                self.state_callback(new_state.name)
                if new_state == actions.Action.idle:
                    self.wait_for_idle.set()
            self.test_connection()

    def _print(self, text: str, source: str = "DC", color="white"):
        self.print_callback(text, source, color)

    def test_connection(self):
        if self.controller is None:
            return False
        try:
            self.controller._pyroBind()
        except Pyro5.errors.CommunicationError:
            return False
        return True

    def try_to_connect(self):
        try:
            self.controller = api.Proxy(
                f"PYRO:dog_controller@{self.host_adress}:44544")
            self.controller._pyroBind()
        except Pyro5.errors.CommunicationError:
            # self._print("Could not connect to remote controller", "DC", "red")
            self.controller = None
            self.is_connected = False
            return False
        self.is_connected = True

    def set_action(self, action: actions.Action):
        self.next_action = action

    def start_loop(self):
        if not self.test_connection():
            self._print("Not connected to remote controller", "DC", "red")
            return
        self.controller.start_loop()
        self._print("Loop started", "DC")

    def stop_loop(self):
        if not self.test_connection():
            self._print("Not connected to remote controller", "DC", "red")
            return
        self.controller.stop_loop()
        self._print("Loop stopped", "DC")

    def start_watcher_if_not_running(self):
        if not self.watcher_running:
            self.watcher_thread = th.Thread(target=self.state_watcher)
            self.watcher_thread.start()

    def state_watcher(self):
        if self.watcher_running:
            self._print("State watcher already running", "DC", "yellow")
            return
        self.watcher_running = True
        while True:
            new_state = self.poll_state()
            if self.state != new_state:
                self._print(
                    f"State changed from {self.state} to {new_state}", "DC")
                self.state = new_state
                self.state_callback(new_state.name)
                if new_state == actions.Action.idle:
                    self.wait_for_idle.set()
            sleep(0.3)
