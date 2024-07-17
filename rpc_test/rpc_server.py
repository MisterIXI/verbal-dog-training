import Pyro5.api as api

@api.expose
class test_class:
    def __init__(self):
        print("test_class created")
        pass

    def test(self):
        return "Hello remote World!"
    
    def print_hello(self, string, number):
        print("Hello local World!")
        print(f"String: {string}, Number: {number}")


daemon = api.Daemon(port=55455)
uri = daemon.register(test_class, "test_class")
print("Ready. URI:", uri)
daemon.requestLoop()