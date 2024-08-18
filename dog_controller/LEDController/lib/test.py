import ctypes


class FaceLightClient:
    def __init__(self):
        self.lib = ctypes.CDLL('./dog_controller/LEDController/lib/libfaceLight_SDK_amd64.so')
        # self.lib = ctypes.CDLL('./libfaceLight_SDK_arm64.so')
        # Function prototypes
        self.lib._ZN15FaceLightClientC1Ev.argtypes = []
        self.lib._ZN15FaceLightClientC1Ev.restype = ctypes.c_void_p
        self.lib._ZN15FaceLightClientD1Ev.argtypes = [ctypes.c_void_p]
        self.lib._ZN15FaceLightClient11setLedColorEjPKh.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
        self.lib._ZN15FaceLightClient7sendCmdEv.argtypes = [ctypes.c_void_p]
        self.lib._ZN15FaceLightClient9setAllLedEPKh.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8)]

        self.obj = self.lib._ZN15FaceLightClientC1Ev()

    def __del__(self):
        self.lib.FaceLightClient_delete(self.obj)

    def set_led_color(self, led_id, r, g, b):
        color = (ctypes.c_uint8 * 3)(r, g, b)
        self.lib.FaceLightClient_setLedColor(self.obj, led_id, color)
        self.lib.FaceLightClient_sendCmd(self.obj)

    def set_all_led(self, r, g, b):
        color = (ctypes.c_uint8 * 3)(r, g, b)
        self.lib.FaceLightClient_setAllLed(self.obj, color)
        self.lib.FaceLightClient_sendCmd(self.obj)
        
if __name__ == '__main__':
    import time
    client = FaceLightClient()
