import time
import logging

from led import LED_NAMES, LED
from server import Server

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    print("Initializing...")
    led_usr1 = LED(LED_NAMES.USR1)
    print("blinking 'usr1'")
    s1 = led_usr1.blink()
    led_usr2 = LED(LED_NAMES.USR2)
    print("blinking 'usr2'")
    s2 = led_usr2.blink()
    if not (s1 and s2):
        print("Initialization failed")
        exit(-1)
    Server.start_all("config.json")
    