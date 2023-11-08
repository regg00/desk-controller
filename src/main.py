from pydantic import BaseModel
from fastapi import FastAPI
from loguru import logger
import random, os, time


UP_PIN = int(os.environ.get("UP_PIN", 18))
DOWN_PIN = int(os.environ.get("DOWN_PIN", 25))
TRIGGER_PIN = int(os.environ.get("TRIGGER_PIN", 23))
ECHO_PIN = int(os.environ.get("ECHO_PIN", 24))
MAX_DISTANCE = int(os.environ.get("MAX_DISTANCE", 220))
TIMEOUT = MAX_DISTANCE * 60


app = FastAPI()


class Desk(BaseModel):
    height: int


def get_sensor_height():
    return random.randint(0, 10)


def move_desk(direction: str, desired_height: int):
    logger.debug(f"Moving desk {direction} to {desired_height}cm")

    if direction == "up":
        relay_to_use = UP_PIN
    elif direction == "down":
        relay_to_use = DOWN_PIN

    logger.debug(f"Pressing {relay_to_use} button")
    # TODO: Press relay_to_use button

    while get_sensor_height() in range(desired_height - 2, desired_height + 2):
        logger.debug(f"Desk is at {get_sensor_height()}cm. Moving it {direction}")

    logger.debug(
        f"Desk at final position {desired_height}cm. Releasing {relay_to_use} button"
    )
    # TODO: Release relay_to_use button


@app.get("/desk/")
def get_desk_height():
    return {"height": get_sensor_height()}


@app.post("/desk/")
def set_desk_height(desk: Desk):
    current_height = get_sensor_height()
    if current_height > desk.height:
        logger.debug("Desk is too high, lowering it")
        move_desk("down", desk.height)

    elif current_height < desk.height:
        logger.debug("Desk is too low, raising it")
        move_desk("up", desk.height)

    else:
        logger.debug("Desk is at the correct height")

    return {"desired_height": desk.height, "current_height": current_height}
