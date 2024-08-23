from time import sleep
import Pyro5.api as api
import Pyro5.errors
from . import actions
import threading as th


class remote_controller():
    def __init__(self, print_callback: callable, state_callback: callable, host_adress="localhost", use_dummy_controller=False) -> None:
        self.print_callback = print_callback
        self.host_adress = host_adress
        self.wait_for_idle = th.Event()
        self.has_finished_connection_attempt = th.Event()
        self.watcher_running = False
        self.state_callback = state_callback
        self.state = actions.Action.idle
        self.is_connected = False
        self.pyro_thread = None
        self.next_action = None
        self.use_dummy_controller = use_dummy_controller
        self.controller = None
        
    def start_pyro_loop(self):
        self.has_finished_connection_attempt.clear()
        if self.pyro_thread is not None and self.pyro_thread.is_alive():
            self._print("Pyro loop already running", "DC", "yellow")
            return
        self._print("Starting pyro thread")
        self.pyro_thread = th.Thread(target=self._pyro_loop)
        self.pyro_thread.start()

    def _pyro_loop(self):
        self.try_to_connect()
        if self.is_connected:
            self._print("Starting pyro loop")
        else:
            self._print("Aborting pyro loop due to failed connection", "DC", "red")
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
            sleep(0.1)

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
        self.has_finished_connection_attempt.clear()
        self._print("Pyro thread attempting to connect...")
        try:
            self.controller = api.Proxy(
                f"PYRO:dog_controller@{self.host_adress}:44544")
            self.controller._pyroBind()
        except Pyro5.errors.CommunicationError:
            # self._print("Could not connect to remote controller", "DC", "red")
            self.controller = None
            self.is_connected = False
            self.has_finished_connection_attempt.set()
            return False
        self.is_connected = True
        self.has_finished_connection_attempt.set()

    def set_action(self, action: actions.Action):
        self.next_action = action
        
    def kill_thread(self):
        if self.pyro_thread is not None:
            self.pyro_thread = None
            
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
