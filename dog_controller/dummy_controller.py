from mimetypes import init
from time import sleep
import Pyro5.api as api
import Pyro5.errors
from actions import Action
import threading as th

@api.expose
class dummy_controller():
    def __init__(self) -> None:
        self.current_action = Action.idle
        self.next_action = Action.idle
        self.start_loop()
        
    def set_action(self, action: Action) -> str:
        if self.current_action != Action.idle:
            print("Cannot set action while current action is not idle")
            return "Cannot set action while current action is not idle"
        self.next_action = action
        print("Action set to " + str(action))
        return "Action set to " + str(action)
    
    def start_loop(self) -> None:
        self.run_loop = True
        self.loop_thread = th.Thread(target=self.update_loop)
        self.loop_thread.start()
    
    def stop_loop(self) -> None:
        self.run_loop = False
    
    def get_current_action(self) -> Action:
        return self.current_action
    
    def update_loop(self) -> None:
        while self.run_loop:
            sleep(3)
            if self.current_action == Action.idle:
                # if idle, loop until next action is set
                if self.next_action != Action.idle:
                    self.current_action = self.next_action
                    self.next_action = Action.idle
                    print("Action started: ", self.current_action)
            elif self.current_action == Action.return_to_idle:
                self.current_action = Action.idle
                print("Returned to idle.")
            else:
                # finished neither idle and return animation
                self.current_action = Action.return_to_idle
                self.next_action = Action.idle
                print("Action finished. Returning to idle.")


if __name__ == "__main__":
    daemon = api.Daemon(port=44544)
    uri = daemon.register(dummy_controller, "dog_controller")
    print("Ready. URI:", uri)
    daemon.requestLoop()