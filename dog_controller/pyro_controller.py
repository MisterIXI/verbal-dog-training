import Pyro5.api as api
import base_controller as bc

daemon = api.Daemon(host="172.21.201.135",port=44544)
uri = daemon.register(bc.BaseController, "dog_controller")
print("Ready. URI:", uri)
daemon.requestLoop()