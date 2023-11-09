from pydantic import BaseModel, Field
from fastapi import FastAPI
from loguru import logger
import os, time
import RPi.GPIO as GPIO
import numpy as np
import warnings


# Setup section
UP_PIN = int(os.environ.get("UP_PIN", 18))
DOWN_PIN = int(os.environ.get("DOWN_PIN", 25))
TRIGGER_PIN = int(os.environ.get("TRIGGER_PIN", 23))
ECHO_PIN = int(os.environ.get("ECHO_PIN", 24))
MAX_DISTANCE = int(os.environ.get("MAX_DISTANCE", 220))
SIT_HEIGHT = int(os.environ.get("SIT_HEIGHT", 71))
STAND_HEIGHT = int(os.environ.get("STAND_HEIGHT", 116))
CALIBRATION = int(os.environ.get("CALIBRATION", 1))
TIMEOUT = MAX_DISTANCE * 60

warnings.filterwarnings("ignore")

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(UP_PIN, GPIO.OUT, initial=1)
GPIO.setup(DOWN_PIN, GPIO.OUT, initial=1)
GPIO.setwarnings(False)

description = """
This API is used to control a desk with a linear actuator.
It uses a HC-SR04 ultrasonic sensor to determine the height of the desk.
The sensor is connected to the Raspberry Pi.
The Raspberry Pi is connected to a relay board which controls the linear actuator.
The relay board is connected to the linear actuator buttons.
"""
app = FastAPI(
    title="Desk Controller API",
    description=description,
    summary="API to control a desk with a linear actuator",
    version="1.0.0",
    contact={"name": "Régis Tremblay Lefrançois", "url": "https://github.com/regg00"},
)


class Desk(BaseModel):
    """The definition of the Desk object

    Args:
        BaseModel (Pydantic.BaseModel): The base model for the Desk object defining the minimum and maximum height of the desk
    """

    height: int = Field(None, ge=71, le=116)


def reject_outliers(data, m=2):
    """Remove outliers from a numpy array

    Args:
        data (numpy.array): The array to remove outliers from
        m (int, optional): The relative scale. Defaults to 2.

    Returns:
        numpy.array: The array without outliers
    """
    return data[abs(data - np.mean(data)) < m * np.std(data)]


def get_sensor_height():
    """Get the height of the desk using the ultrasonic sensor

    Returns:
        int: The height of the desk in cm
    """

    # Take 10 measurements and return the mean value without outliers.
    measurements = []
    for _ in range(10):
        GPIO.output(TRIGGER_PIN, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(TRIGGER_PIN, GPIO.LOW)

        while GPIO.input(ECHO_PIN) == 0:
            pulse_start_time = time.time()
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = int(round(pulse_duration * 17150, 2))
        measurements.append(distance)
        time.sleep(0.06)

    measurements = np.asarray(measurements)
    logger.debug(f"Raw measurements: {measurements}")

    # Remove outliers if any
    cleaned_up_measurements = reject_outliers(measurements)

    try:
        mean_value = int(np.nanmean(cleaned_up_measurements))
    except ValueError:
        mean_value = int(np.nanmean(measurements))

    logger.info(f"Height: {mean_value}")
    return mean_value


def move_desk(desired_height: int):
    """Move the desk to the desired height

    Args:
        desired_height (int): The desired height of the desk in cm
    """
    # Determine which button to press
    current_height = get_sensor_height()

    if current_height > desired_height:
        relay_to_use = DOWN_PIN
    elif current_height < desired_height:
        relay_to_use = UP_PIN
    else:
        logger.debug("Desk is at the correct height")

    logger.debug(f"Pressing {relay_to_use} button")

    GPIO.output(relay_to_use, GPIO.LOW)

    while (
        not desired_height - CALIBRATION
        <= get_sensor_height()
        <= desired_height + CALIBRATION
    ):
        logger.debug(
            f"Desk is at {get_sensor_height()}cm. Moving it to {desired_height}cm"
        )

    logger.debug(
        f"Desk at final position {desired_height}cm. Releasing {relay_to_use} button"
    )
    GPIO.output(relay_to_use, GPIO.HIGH)


@app.get("/desk/")
def get_desk_height():
    """Return the height of the desk in cm

    Returns:
        dict: The height of the desk in cm
    """
    return {"height": get_sensor_height()}


@app.get("/cleanup/")
def cleanup():
    """Cleanup the GPIO pins

    Returns:
        dict: A message confirming that the pins have been cleaned up
    """
    GPIO.cleanup()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(UP_PIN, GPIO.OUT, initial=1)
    GPIO.setup(DOWN_PIN, GPIO.OUT, initial=1)
    return {"message": "pins have been cleared"}


@app.post("/desk/preset/{preset_id}")
def set_preset_height(preset_id: int):
    """Set the desk to a preset height

    Args:
        preset_id (int): The id of the preset to use

    Returns:
        dict: A confirmation message and the current height of the desk
    """
    if preset_id == 1:
        move_desk(SIT_HEIGHT)
    elif preset_id == 2:
        move_desk(STAND_HEIGHT)
    else:
        logger.debug(f"Preset {preset_id} does not exist")

    return {"preset_id": preset_id, "current_height": get_sensor_height()}


@app.post("/desk/")
def set_desk_height(desk: Desk):
    """Set the desk to the desired height

    Args:
        desk (Desk): The desk object containing the desired height

    Returns:
        dict: A confirmation message and the current height of the desk
    """
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
