import Pyro5.api as api

test_class = api.Proxy("PYRO:test_class@localhost:55455")
print(test_class.test())
test_class.print_hello("coolstring", 42)