from pydantic import BaseModel
from fastapi import FastAPI
from loguru import logger
import os, time
import RPi.GPIO as GPIO


UP_PIN = int(os.environ.get("UP_PIN", 18))
DOWN_PIN = int(os.environ.get("DOWN_PIN", 25))
TRIGGER_PIN = int(os.environ.get("TRIGGER_PIN", 23))
ECHO_PIN = int(os.environ.get("ECHO_PIN", 24))
MAX_DISTANCE = int(os.environ.get("MAX_DISTANCE", 220))
SIT_HEIGHT = int(os.environ.get("SIT_HEIGHT", 70))
STAND_HEIGHT = int(os.environ.get("STAND_HEIGHT", 120))

TIMEOUT = MAX_DISTANCE * 60


app = FastAPI()


class Desk(BaseModel):
    height: int


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
def get_sensor_height():
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
    return int(distance)


GPIO.setmode(GPIO.BCM)

# set TRIGGER_PIN to OUTPUT mode
GPIO.setup(TRIGGER_PIN, GPIO.OUT)

# set ECHO_PIN to INPUT mode
GPIO.setup(ECHO_PIN, GPIO.IN)

GPIO.setup(UP_PIN, GPIO.OUT, initial=1)
GPIO.setup(DOWN_PIN, GPIO.OUT, initial=1)


def move_desk(desired_height: int):
    current_height = get_sensor_height()

    if current_height > desired_height:
        relay_to_use = DOWN_PIN
    elif current_height < desired_height:
        relay_to_use = UP_PIN
    else:
        logger.debug("Desk is at the correct height")

    logger.debug(f"Pressing {relay_to_use} button")
    GPIO.output(relay_to_use, GPIO.LOW)

    while get_sensor_height() != desired_height:
        logger.debug(
            f"Desk is at {get_sensor_height()}cm. Moving it to {desired_height}cm"
        )

    logger.debug(
        f"Desk at final position {desired_height}cm. Releasing {relay_to_use} button"
    )
    GPIO.output(relay_to_use, GPIO.HIGH)


@app.get("/desk/")
def get_desk_height():
    return {"height": get_sensor_height()}


@app.post("/desk/preset/{preset_id}")
def set_preset_height(preset_id: int):
    if preset_id == 1:
        move_desk(SIT_HEIGHT)
    elif preset_id == 2:
        move_desk(STAND_HEIGHT)
    else:
        logger.debug(f"Preset {preset_id} does not exist")

    return {"preset_id": preset_id, "current_height": get_sensor_height()}


@app.post("/desk/")
def set_desk_height(desk: Desk):
    current_height = get_sensor_height()
    if current_height > desk.height:
        logger.debug("Desk is too high, lowering it")
        move_desk(desk.height)

    elif current_height < desk.height:
        logger.debug("Desk is too low, raising it")
        move_desk(desk.height)

    else:
        logger.debug("Desk is at the correct height")

    return {"desired_height": desk.height, "current_height": current_height}
