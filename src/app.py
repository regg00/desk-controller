from flask import Flask, make_response
from flask_restful import Resource, Api, reqparse
import RPi.GPIO as GPIO
import time
import json

GPIO_PRESET_1 = 25   # sit
GPIO_PRESET_4 = 24   # stand


GPIO.cleanup()

# GPIO setup
GPIO.setmode(GPIO.BCM)
#removing the warings
GPIO.setwarnings(False)

#setting the mode for all pins so all will be switched on
GPIO.setup(GPIO_PRESET_1, GPIO.OUT)
GPIO.setup(GPIO_PRESET_1, GPIO.LOW)
GPIO.setup(GPIO_PRESET_4, GPIO.OUT)
GPIO.setup(GPIO_PRESET_4, GPIO.LOW)

app = Flask(__name__)
api = Api(app)
state = None

# API definition
class DeskController(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('position', type=str, help='Which position to set the desk to. Valide values are sit or stand.')

    # Set the position
    def set_position(self, position: str) -> int:
        global state
        if position == 'sit':
            GPIO.output(GPIO_PRESET_1,  GPIO.HIGH)
            time.sleep(1)
            GPIO.output(GPIO_PRESET_1,  GPIO.LOW)
            state = 'sit'

        if position == 'stand':
            GPIO.output(GPIO_PRESET_4,  GPIO.HIGH)
            time.sleep(1)
            GPIO.output(GPIO_PRESET_4,  GPIO.LOW)
            state = 'stand'


    def get(self):
        global state
        if state == 'stand':
            result = {'is_active': True}
        else:
            result = {'is_active': False}
        response = make_response(json.dumps(result))
        response.headers['Content-Type'] = 'application/json'
        return response




    # POST to set the height
    def post(self):
        args = self.parser.parse_args()
        self.set_position(args.position)

        return args, 201

class GPIOCleanup(Resource):
    def get(self):
        GPIO.cleanup()

        return {"message":"pins have been cleared"},200

class GPIOSetup(Resource):
    def get(self):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)

        #removing the warings
        GPIO.setwarnings(False)

        #setting the mode for all pins so all will be switched on
        GPIO.setup(GPIO_PRESET_1, GPIO.OUT)
        GPIO.setup(GPIO_PRESET_4, GPIO.OUT)
        GPIO.setup(GPIO_PRESET_1, GPIO.LOW)
        GPIO.setup(GPIO_PRESET_4, GPIO.LOW)

        return {"message":"pins have been setup"},200

# Everything is under the root for now
api.add_resource(DeskController, '/')
api.add_resource(GPIOCleanup, '/cleanup')
api.add_resource(GPIOSetup, '/setup')


# Run in debug mode
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)