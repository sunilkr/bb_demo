import time
import logging

class LED_NAMES(object):
    USR1 = "/sys/class/leds/beaglebone:green:usr1/brightness"
    USR2 = "/sys/class/leds/beaglebone:green:usr2/brightness"

    @classmethod
    def get(cls, name):
        if name.upper() == "USR1":
            return cls.USR1
        elif name.upper() == "USR2":
            return cls.USR2
        else:
            return None
            

class LED(object):
    def __init__(self, name):
        super(object, self)
        self.file = name
        self.logger = logging.getLogger(str(self.__class__))

    def is_on(self):
        try:
            with open(self.file, "r") as lfh:
                last_b = lfh.read()
                if last_b == "1":
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.exception("Error reading file {0} --> ".format(self.file))
            return None


    def turn_on(self):
        try:
            with open(self.file, "w") as lfh:
                lfh.write("1")
            return True
        except Exception as e:
            self.logger.exception("Error reading file {0} --> ".format(self.file))
        return False
    

    def turn_off(self):
        try:
            with open(self.file, "w") as lfh:
                lfh.write("0")
            return True
        except Exception as e:
            self.logger.exception("Error reading file {0}".format(self.file))
        return False


    def blink(self, count=2, delay=0.5):
        if not self.turn_off():
            return False

        status = True
        for i in range(count):
            status = self.turn_on()
            time.sleep(delay)
            status = self.turn_off()
            time.sleep(delay)
        return status

