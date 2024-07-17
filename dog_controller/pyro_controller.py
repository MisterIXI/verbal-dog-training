import Pyro5.api as api
import base_controller as bc

daemon = api.Daemon(port=55455)
uri = daemon.register(bc.BaseController, "dog_controller")
print("Ready. URI:", uri)
daemon.requestLoop()