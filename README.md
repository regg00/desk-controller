# A desk height controller

[![balena deploy button](https://www.balena.io/deploy.svg)](https://dashboard.balena-cloud.com/deploy?repoUrl=https://github.com/regg00/desk-controller)

This is a simple desk height controller using a relay to simulate button presses on the control board.

#### There's soldering needed for this to work.

## Requirements
* Raspberry Pi
* [HC-SR04 Ultrasonic Distance Sensor](https://www.sparkfun.com/products/15569)
* [2 Channel Relay Module](https://www.amazon.ca/SunFounder-Channel-Shield-Arduino-Raspberry/dp/B00E0NTPP4?th=1)
* Breabord
* Some cables
* Soldering iron
* Balena account

## Schematics
TODO: Insert schematics

### How to push your code with Balena:
```bash
cd desk-controller/
balena push <FLEET_NAME>
```

## References
* [balena-cli](https://www.balena.io/docs/reference/cli/)
* [balena-dashboard](https://dashboard.balena-cloud.com)
* [balena-link](https://balena.io/)
* [devices-supported](https://www.balena.io/docs/reference/hardware/devices/)
* [gettingStarted-link](https://www.balena.io/docs/learn/getting-started/raspberrypi3/python/)


