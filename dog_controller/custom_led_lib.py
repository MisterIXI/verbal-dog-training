import socket
import threading as th
from time import sleep


class LedController:
    def __init__(self) -> None:
        self.animation_thread = None
        self.animation_thread_running = False
        pass

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    OFF = (0, 0, 0)

    UDP_IP = "192.168.123.13"
    UDP_PORT = 8889

    FULL = "eeeeeeee"
    ZERO = "88888888"
    EMPTY = "00000000"

    LED_CYCLE_SLEEP_DURATION = 0.01

    def _uint8_to_special_code(self, value: int) -> str:
        """Convert a uint8 value to the special hex/binary code required for the UDP package.

        Args:
            value (uint8): 0-255 value to convert

        Returns:
            str: The 8 character long hex code to place in the UDP package
        """
        mask = format(value, '08b')
        mask = mask.replace("0", "8")
        mask = mask.replace("1", "e")
        return mask

    def _get_empty_data(self) -> str:
        """Creates the empty data for the UDP package."""
        return [
            [
                self.EMPTY for _ in range(3)
            ] for _ in range(12)
        ]

    def _convert_list_to_hexstring(self, leds: list) -> str:
        data = ""
        for led in leds:
            for color in led:
                data += str(color)
        return data

    def _build_and_send_data(self, data: list[list]) -> None:
        hex_string = self._convert_list_to_hexstring(data)
        # send via udp
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes.fromhex(hex_string), (self.UDP_IP, self.UDP_PORT))

    def set_led_single(self, led_id: int, color: tuple[int, int, int]) -> None:
        """Set a single led to a specified rgb color.

        Args:
            led_id (int): (0-11) id of led
            r (uint8): (0-255) red component
            g (uint8): (0-255) green component
            b (uint8): (0-255) blue component
        """
        leds = self._get_empty_data()
        leds[led_id][0] = self._uint8_to_special_code(color[0])
        leds[led_id][1] = self._uint8_to_special_code(color[1])
        leds[led_id][2] = self._uint8_to_special_code(color[2])
        self._build_and_send_data(leds)

    def set_led_all(self, color: tuple[int, int, int]) -> None:
        r = self._uint8_to_special_code(color[0])
        g = self._uint8_to_special_code(color[1])
        b = self._uint8_to_special_code(color[2])
        self._build_and_send_data([
            [
                r, g, b
            ] for _ in range(12)
        ])

    def clear_led_all(self) -> None:
        self.set_led_all(self.OFF)

    def _uint8_lerp(self, a: int, b: int, t: float) -> int:
        a = max(0, min(255, a))
        b = max(0, min(255, b))
        return int(max(0, min(255, a + (b - a) * t)))

    def start_breathing_color(self, cycle_duration: float, colorA: tuple[int, int, int], colorB: tuple[int, int, int]) -> None:
        """Starts a breathing animation between two colors. The cycle_duration defines the time for one way of the cycle.

        Args:
            cycle_duration (float): Time in seconds for one way of the cycle
            colorA (tuple[int, int, int]): (values 0-255) RGB color A
            colorB (tuple[int, int, int]): (values 0-255) RGB color B
        """
        if self.animation_thread is not None and self.animation_thread.is_alive():
            self.animation_thread_running = False
            self.animation_thread.join()

        self.animation_thread = th.Thread(
            target=self._continous_breathing, args=(cycle_duration, colorA, colorB))
        self.animation_thread_running = True
        self.animation_thread.start()

    def stop_breathing_color(self, wait_for_end: bool = False) -> None:
        """Stops the breathing animation."""
        self.animation_thread_running = False
        if wait_for_end and self.animation_thread is not None and self.animation_thread.is_alive():
            self.animation_thread.join()
        self.clear_led_all()

    def _continous_breathing(self, cycle_duration: float, colorA: tuple[int, int, int], colorB: tuple[int, int, int]) -> None:
        """Traps the program in a loop (intended to use with a thread) until self.animation_thread_running is set to False. It interpolates between two colors in with a duration of cycle_duration for one way. To return to colorA after one full cycle, cycle_duration*2 time has passed.

        Args:
            cycle_duration (float): Time in seconds for one way of the cycle
            colorA (tuple[int, int, int]): (values 0-255) RGB color A
            colorB (tuple[int, int, int]): (values 0-255) RGB color B
        """
        a = (
            max(0, min(255, colorA[0])),
            max(0, min(255, colorA[1])),
            max(0, min(255, colorA[2])),
        )
        b = (
            max(0, min(255, colorB[0])),
            max(0, min(255, colorB[1])),
            max(0, min(255, colorB[2])),
        )
        t = 0
        counting_up: bool = True
        while self.animation_thread_running:
            self.set_led_all((

                self._uint8_lerp(a[0], b[0], t / cycle_duration),
                self._uint8_lerp(a[1], b[1], t / cycle_duration),
                self._uint8_lerp(a[2], b[2], t / cycle_duration),
            ))
            sleep(self.LED_CYCLE_SLEEP_DURATION)
            if counting_up:
                t += self.LED_CYCLE_SLEEP_DURATION
                if t >= cycle_duration:
                    t = cycle_duration
                    counting_up = False
            else:
                t -= self.LED_CYCLE_SLEEP_DURATION
                if t <= 0:
                    t = 0
                    counting_up = True
