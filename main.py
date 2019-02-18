import time

path_tmpl = "/sys/class/leds/beaglebone:green:{0}/brightness"

def blink_led(name, count=2, delay=0.5):
    led_file = path_tmpl.format(name)
    last_b = 0
    try:
        with open(led_file, "r") as lfh:
            last_b = lfh.read()
    except Exception as e:
        print("Error reading file {0}, err: {1}".format(led_file, e))
        return -1

    for i in range(count):
        try:
            with open(led_file, "w") as lfh:
                lfh.write("1")
            #print("LED should be ON")
            time.sleep(delay)
            with open(led_file, "w") as lfh:
                lfh.write("0")
            #time.sleep(1)
            #print("LED should be OFF")
        except Exception as e:
            print("Error writing file {0}, err: {1}".format(led_file, e))
            return -2
        time.sleep(delay)

    return 0
    #time.sleep(delay)


if __name__ == "__main__":
    print("blinking 'usr1'")
    blink_led("usr1")
    time.sleep(1)
    print("blinking 'usr2'")
    blink_led("usr2")
