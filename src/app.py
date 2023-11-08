import RPi.GPIO as GPIO
import os
import time

TRIGGER_PIN = int(os.environ.get("TRIGGER_PIN"))
ECHO_PIN = int(os.environ.get("ECHO_PIN"))
MAX_DISTANCE = int(os.environ.get("MAX_DISTANCE"))
TIMEOUT = MAX_DISTANCE * 60


# Obtain pulse time of a pin under TIMEOUT
def pulse_in(pin: int, level, TIMEOUT: int):
    t0 = time.time()
    while GPIO.input(pin) != level:
        if (time.time() - t0) > TIMEOUT * 0.000001:
            return 0
    t0 = time.time()
    while GPIO.input(pin) == level:
        if (time.time() - t0) > TIMEOUT * 0.000001:
            return 0
    pulse_time = (time.time() - t0) * 1000000
    return pulse_time


# Get the measurement results of ultrasonic module,with unit: cm
def get_sonar():
    # make TRIGGER_PIN output 10us HIGH level
    GPIO.output(TRIGGER_PIN, GPIO.HIGH)

    # 10us
    time.sleep(0.00001)

    # make TRIGGER_PIN output LOW level
    GPIO.output(TRIGGER_PIN, GPIO.LOW)

    # read plus time of ECHO_PIN
    ping_time = pulse_in(ECHO_PIN, GPIO.HIGH, TIMEOUT)

    # calculate distance with sound speed 340m/s
    distance = ping_time * 340.0 / 2.0 / 10000.0
    return distance


def setup():
    # use PHYSICAL GPIO Numbering
    GPIO.setmode(GPIO.BCM)

    # set TRIGGER_PIN to OUTPUT mode
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)

    # set ECHO_PIN to INPUT mode
    GPIO.setup(ECHO_PIN, GPIO.IN)


def loop():
    while True:
        distance = get_sonar()  # get distance
        print("The distance is : %.2f cm" % (distance))


if __name__ == "__main__":
    print("Program is starting...")
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
