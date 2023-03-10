# Rover

This will be the playground for my rover control software. I've never done anything like this, so I anticipate learning a lot and making more mistakes than things I get right, but the goal is to get something that is... functional. Self-healing in the case of a crash would be nice as well, but we're gonna have to see about that one. That will probably be at least a consequence of the rover getting shutdown periodically, so it'll boot to a known state each time. So long as I don't break that, should be fine.

The rover design goal is to build a remote-controlled vehicle, that is capable of operating in arbitrarily remote enviroments. Obviously, that is limited to places I can signal, so that is limited in reality to places that get mobile internet reception.  

**This is not a build guide. This is ONLY a place for me to store and back up my code, and take notes for myself. If you want to replicate this project, it will not be easy!**


# Software

The Rover hosts software, which I'm building right now, and has the following stack:
- Nginx
  - handles authentication and URL routing
- Rover API server
  - Provides API access to the rover. 
  - Authenticate requests, parse JSON input from the operator and pass commands to be executed to the hardware controller.
  - This ensures that the root-privilege hardware controller is not exposed directly to the open web
- Hardware control backend server
  - Interfaces with the GPIO pins (requires root to do this)
  - runs its own HTTP server, with its own API. This, however, runs as root and only listens to localhost, so is not publicly accessible.
- Camera WebRTC host, `uv4l`
  - Again, running its own server. This one has to be publicly accessible, though.

I also have "Mission Control". This is hosted on my home server, and acts as a portal to access the rover. The rover will periodically update mission control with its IP address, and upload logs for storage while taking data. Mission control runs this, much simpler, stack:
- Nginx
- Base station flask server

## TODO
- Write a motor interface - xbox controllers?
  - Possibly, I might need some kinematics algorithm to make sure I'm making good use of the tracks
- WebRTC rover control? May have lower latency.
- Secure WebRTC with the API token


# Usage 

The rover should be roughly self-explanatory to users, but the backed is already somewhat convoluted. I will have a subsection dedicated to each layer, roughly in order of how commands are issued, and a try to include a description of where each module fits in to the rest of the code.

## Mission Control

Mission control is a base station hosted on my [website](https://wildjames.com/base/). This page acts as a waiting room for waking the rover. To save power, the rover periodically turns on, checks if anyone is asking it to stay awake, and either goes back to sleep or stays on. The base station page has a small interface where a user can supply the URL for a rover (by default, this is the proxy maintained by mission control) and an API token that must be fetched from the rover itself. By either hitting enter on the token box or clicking the white circle, the page will begin to ping the rover, asking it to stay awake on its next boot. The rover will stay online then for as long as that page is open or pinging the server, which can be disabled again by clicking the indicator or hitting enter on the token box again. After 5 minutes of inactivity, the rover will turn itself off again.

The rover will also upload readings to the rover periodically. It should have a set of environmental sensors (temperature, sunlight, that kind of thing) that get read at some interval and stored locally temporarily. Mission control acts as long term storage for this data, and as a place to see graphs of it.

TODO: Mission control should have graphs of readings that the rover uploads

### API endpoints

#### `/receive_data`

Receive a POST request containing a log file, of the form:
```
<variable>,<timestamp>,<value>
<variable>,<timestamp>,<value>
```
The data are stored by mission control.

Returns "OK" on successful execution.


## Rover Control Page

The rover hosts a control center, from which users can see the video feed and send commands to the hardware. This is all written in JavaScript and HTML. 

Commands are sent to the rover using the rovers' control API endpoints, and the video is streamed over WebRTC. **Note that, as far as I can tell, the video streaming only really works on Chrome!**

To use the rover, enter the API token at the top and hit enter. The buttons should change colour to reflect the current status of the rover, or you should get an alert telling you your API token was invalid.

## Rover API server

The rover hosts a request scrubber. It takes requests, extracts the relevant keys from the posted JSON, makes sure the commands are valid, then creates and posts a new request to the hardware controller. This setup ensures that the public doesn't have access to the hardware control server directly, and should make it less susceptible to attacks.

This module obviously has a lot of API endpoints.

### API endpoints

All requests should be authenticated by supplying the API token as a Bearer token in the request headers.

#### `/ping`, `GET`

Acts as a test endpoint. No data are returned, only a {"message": "pong"}, but that is only returned if the API token correctly authenticates the request. 

Acts as a keepalive message.


#### `/system_info`, `GET`

Return a JSON dictionary containing information on the state of various rover systems. 

Acts as a keepalive message.

Returns data structure:
```
{
  "led_data": {
    "num_leds": int,
    "led_states": List[(index, state)],
  },
  "motor_data": {
    "num_motors": int,
    "motor_states": [
      {
        "pin": int,
        "min_pulse": int,
        "max_pulse": int,
        "throttle": float,
        "started": int,
      },
    ]
  },
  "sleep_data": {
    "sleep_time": float,
    "enable_sleep": int,
  },
  "environment_logger": {
    "log_interval": float,
    "log_purge_interval": float,
    "upload_interval": float,
  },
}
```

#### `/config`, POST

Sets any internal rover variables. 

Acts as a keepalive message.

Options (can be present in any combination):
```
"sleep_time": float,
"sleep_enable": int/bool,
```


#### `/led_control`, POST

Set the LED pins to match the given state.

Acts as a keepalive message.

Command JSON is a list of two-value lists, of the form:
```
{
  [
    [<index, int>, <state, int>]
  ]
}
```



#### `/motor_command`, POST

Control the motor. You must submit either a single command, or a list of commands to execute. If multiple commands are given, they are executed in order immediately after one another.

Commands, and their payloads:
```
{
  "command": "motor_init",
  "index": int,
}
```
Initialises a motor. This will leave the motor in a state where it can throttle up.

```
{
  "command": "motor_close",
  "index": int,
}
```
Close a motor controller. This throttles down, turns off the GPIO pin, and releases it for use. 


```
{
  "command": "",
  "index": int,
}
```


## Rover Backend server

This is essentially a mirror of the rover API server, but with access to the hardware controls and root privileges. I won't detail the API, since it's the same as the API server.

Note that this also handles uploading environment logs to mission control. That is done by spawning threads on start with timers. 


# Hardware

Just some thoughts and ideas.

## Communication

This [4G base station](https://www.waveshare.com/product/sim7600g-h-4g-dtu.htm) is about the cost of the chip, but comes with some nice extras. Might gobble some power, though: 
- Operating voltage	7 ~ 36V DC
- Operating current
  - idle: 10~30mA @12V
  - transmit: 80~450mA @12V (depending on the network condition)
If I'm running off a LiPo bank, the voltage won't be an issue, but drawing 30mA even when idle might be a bit much. When powered down, I can cut the power to it completely.

I should 100% get some apple air tags and fuse them to the chassis somehow, as a backup.

## Motion

Treads can be [bought](https://www.aliexpress.com/item/32876365731.html) - they're not *cheap*, but they're not overly expensive. I would probably want to fabricate the main body of the rover in the shop. Plastic < metal, probably? More weatherproof. I keep gravitating towards [this one](https://www.aliexpress.com/item/4000187862847.html) ([build doc](https://gitnova.com/#/Robot/FrameChassis/4WDDampingCar/4WDDampingCar))

Hell yes. I bagged a hoverboard for ??50, which gives me two high-torque brushless hub motors and a whopping great battery - jackpot. You can pick these up for a pittance, so getting another two motors for the read tyres would be no issue.

## Power

If I eyeball total power usage (when active) of the compute parts as about 5W for the raspberry pi, 400mA for the modem to give 3.6W while transmitting, call that 4W, I estimate around 10W power draw while the computers are all on and communicating. This is less than the 20W of the solar panel, so we will still be able to charge (albeit slowly) while all the computing is running at full tilt. 

However, the motors are 250W *each*, so will drain the battery very quickly. If we go 2-wheel drive, we're looking at a peak output of 500W. Realistically, most of the time won't be running this hard, but take that as a worst-case scenario. A 4Ah lipo battery at 22.7V holds approximately 100Wh of power, which would run this system at full whack for only about 12 minutes. I have plenty of room to add more batteries, but really I don't want to buy more than 4, and that's still only about 45 minutes of hard driving... 

For reference, I can find 20W solar panels on [aliexpress](https://www.aliexpress.com/item/1005004546004726.html) that are specced as `300x145x3MM 20W` and probably around 1kg, so totally doable on the rover. If I splash out and put wings on the thing, I *could* overhang the sides and put two on - but I think it wouldn't be worth it and would be asking for trouble. [Amazon](https://www.amazon.co.uk/Waterproof-Portable-Starter-Monocrystalline-Controller/dp/B0B9T4V3JF/) has [comparable](https://www.amazon.co.uk/Monocrystalline-Waterproof-Maintainer-Motorhomes-Motorcycle/dp/B08QHRWK4M/) things, that are far more likely to be authentic.

From this estimate, I would guess that a relatively standard 4,000mAh LiPo (which typically costs about ??100, ouch!) would run the thing for about an hour; (4 Ah * 12V) / 40W = 72 minutes. a 6C motor is aroun ??60, here is a [two-pack](https://www.amazon.co.uk/HRB-4000mAh-Battery-Quadcopter-Helicopter/dp/B06XT6L382) on Amazon, or [one 6s](https://www.hobbyrc.co.uk/gnb-4000mah-6s-50c-lipo-battery) on hobbyking.

I should also get something to function as a mini UPS for the controller and modem. That way, I can still communicate with the rover even if I run the main batteries all the way down, which is likely. Especially if there's a run of poor weather. [UPS](https://www.waveshare.com/ups-module-3s.htm). That UPS turned out to be not very good. Instead, I'm going to go down the route of having an Arduino that cuts power to the pi when its idle

## Camera

The pi has a camera module, but I would probably be better off with a mid-tier USB webcam instead. Bulkier, but that's not an issue. [here](https://www.aliexpress.com/item/1005002165612156.html) is a gimbal that I can mount it on - probably very worthwhile for QoL on sustained drives. 

# Notes, TODO

Hardware interface works, using a mini server accessible only on localhost.

https://www.linux-projects.org/uv4l/installation/
This works on here: http://192.168.1.170:1002/ I have cloned over the web code, it's in `facedetection`. I think it's best to ditch the flask frontend, and just use javascript to handle the web interface instead. Should be easier, and I won't have to run two flask servers!

`uv4l` server can be configured with this file and service:
```
rover@RoverPi:/usr/local/www/rover $ sudo nano /etc/uv4l/uv4l-raspicam.conf
rover@RoverPi:/usr/local/www/rover $ sudo service uv4l_raspicam restart
```

I think it may be better to stream states and commands over WebRTC similar to video... This may be somewhat tricky to learn though.



# Setup, prerequisites

Before anything else, 
```
sudo apt-get update && sudo apt-get upgrade -y
curl https://sh.rustup.rs -sSf | sh
```
There are then some apt-get installs to do:
```
sudo apt-get install -y \
  build-essential libpq-dev libssl-dev libffi-dev nginx \
  libatlas-base-dev gcc libssl-dev python3-dev python3-pip \
  libjpeg62 musl-dev zlib1g-dev libjpeg-dev openssl git gunicorn
```
Make the log directory for later,
```
mkdir /home/rover/logs
```
And finally, install the python packages we are going to need:
```
pip install -U pip
pip install -r requirements.txt
```

Set up the git instance with an SSH key. Then, clone this repo.


## Start the hardware controller:

The hardware is controlled by its own script. This has to be run with `sudo` privileges and is interfaced with HTTP, so really shouldn't be exposed to the internet. So, it's only available on localhost, where a middleware API will forward commands to it. It's located in the script [`controller_server.py`](controllers/controller_server.py), and I've written a service configuration that should keep it running. 

First, check the configuration to make sure it will run ok. Then, 
```
sudo cp setup/hardware_controller.service /etc/systemd/system/
sudo systemctl enable hardware_controller
sudo systemctl start hardware_controller
```


## Start the Flask API server

The hardware server is not exposed to the network. Rather, it is interacted with via a second flask server. This is a security feature - I don't want a sudo-level server that any random person can access, even if they do need API tokens. 

This has a service to keep it going, so setup is similar to the backend controller
```
sudo cp setup/flask_middleware.service /etc/systemd/system/
sudo systemctl enable flask_middleware
sudo systemctl start flask_middleware
```


## Install and configure nginx

Really, we should get a proper signed SSL certificate. However, as a stopgap we can get a self-signed one.
To create a new self-signed SSL certificate, with this command:
```
sudo mkdir /etc/nginx/SSL
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/SSL/selfsigned.key -out /etc/nginx/SSL/selfsigned.crt
```
Note that this is not ideal for deployment, but will do for testing.

Then, set up the flask app to be run by nginx. To do this, I have provided a configuration in `setup/rover_server.nginx`. Tweak that, and move it to `/etc/nginx/sites-available/`
```
sudo cp setup/rover_server.nginx /etc/nginx/sites-available/
```
Then, enable the site by making a symlink in the `sites-enabled` directory
```
cd /etc/nginx/sites-enabled
sudo ln -s /etc/nginx/sites-available/rover_server.nginx .
```
and reload nginx
```
sudo systemctl reload nginx
```


## Install `uv4l`
[Original instructions](https://www.linux-projects.org/uv4l/installation/)

```
sudo rpi-update
echo /opt/vc/lib/ | sudo tee /etc/ld.so.conf.d/vc.conf
sudo ldconfig
```

Then, using the `sudo raspi-config` tool, enable legacy camera support. While you're there, increase the GPU memory to its maximum value.
Then, add the repo to `apt`
```
curl https://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | sudo apt-key add -
echo "deb https://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" | sudo tee /etc/apt/sources.list.d/uv4l.list
sudo apt-get update
sudo apt-get install -y uv4l uv4l-raspicam
sudo apt-get install -y uv4l uv4l-server uv4l-uvc uv4l-server uv4l-webrtc uv4l-xmpp-bridge
```

Then, install my configuration for the webRTC server and reboot the computer to force a clean state
```
sudo cp setup/uv4l-raspicam.conf /etc/uv4l/
sudo reboot
```
