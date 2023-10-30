from flask import Flask, request
from flask_restful import Resource, Api, reqparse

# Relay pins
GPIO_RELAY_UP = 12
GPIO_RELAY_DOWN = 11

app = Flask(__name__)
api = Api(app)

# Validate that the height argument is a int
parser = reqparse.RequestParser()
parser.add_argument('height', type=int, help='Height of the desk in mm')

# Get the actual height from the sensor
def get_height_from_sensor() -> int:
    return 35

# Set the height
def set_height(height: int) -> int:
    return height


# API definition
class DeskController(Resource):
    # GET the current height
    def get(self):        
        return {'height':get_height_from_sensor()}, 200
    
    # POST to set the height    
    def post(self):
        args = parser.parse_args()
        return args, 201
    
        
# Everything is under the root for now
api.add_resource(DeskController, '/')


# Run in debug mode
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)