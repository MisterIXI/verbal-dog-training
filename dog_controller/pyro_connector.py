import Pyro5.api as api
import Pyro5.errors
from . import actions

class remote_controller():
    def __init__(self, print_callback: callable, host_adress="localhost") -> None:
        self.print_callback = print_callback
        self.host_adress = host_adress
        self.try_to_connect()
    
    def _print(self, text: str, source: str = "DC", color="white"):
        self.print_callback(text, source, color)
        
    def is_connected(self):
        if self.controller is None:
            return False
        try:
            self.controller._pyroBind()
        except Pyro5.errors.CommunicationError:
            return False
        return True
    
    def try_to_connect(self):
        try:
            self.controller = api.Proxy(f"PYRO:dog_controller@{self.host_adress}:55455")
            self.controller._pyroBind()
        except Pyro5.errors.CommunicationError:
            # self._print("Could not connect to remote controller", "DC", "red")
            self.controller = None
            return False
    
    def set_action(self, action: actions.Action):
        if not self.is_connected():
            self._print("Not connected to remote controller", "DC", "red")
            return
        response:str = self.controller.set_action(action)
        if response.startswith("Cannot"):
            self._print(response, "DC", "yellow")
        else:
            self._print(response, "DC")
    
    def start_loop(self):
        if not self.is_connected():
            self._print("Not connected to remote controller", "DC", "red")
            return
        self.controller.start_loop()
        self._print("Loop started", "DC")
    
    def stop_loop(self):
        if not self.is_connected():
            self._print("Not connected to remote controller", "DC", "red")
            return
        self.controller.stop_loop()
        self._print("Loop stopped", "DC")
    
    def poll_state(self) -> actions.Action:
        if not self.is_connected():
            self._print("Not connected to remote controller", "DC", "red")
            return actions.Action.idle
        return self.controller.get_current_action()