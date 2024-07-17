import Pyro5.api as api
ip = "172.21.201.135"
c = api.Proxy(f"PYRO:dog_controller@{ip}:44544")
