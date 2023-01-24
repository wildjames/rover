# Rover

This will be the playground for my rover control software. I've never done anything like this, so I anticipate learning a lot and making more mistakes than things I get right, but the goal is to get something that is... functional. Self-healing in the case of a crash would be nice as well, but we're gonna have to see about that one.

The rover design goal is to build a remote-controlled vehicle, that is capable of operating in arbitrarily remote enviroments. Obviously, that is limited to places I can signal, so that is limited in reality to places that get mobile internet reception. 


# Software

The control software I'm building right now has the following stack:
- Apache2 server
  - handles authentication and URL routing
- Flask app
  - Frontend code, web interface
  - parses JSON input from the operator and passes commands to be executed to the hardware controller
- Hardware controller script(s?)
  - Interfaces with the GPIO pins (requires root to do this)
  - runs its own HTTP server, with its own API. This, however, runs as root so is not publicly accessible.
- Camera WebRTC host, `uv4l`
  - Again, running it's own server. This one has to be publicly accessible, though.

# Hardware

Just some thoughts and ideas.

## Communication

This [4G base station](https://www.waveshare.com/product/sim7600g-h-4g-dtu.htm) is about the cost of the chip, but comes with some nice extras. Might gobble some power, though: 
- Operating voltage	7 ~ 36V DC
- Operating current
  - idle: 10~30mA @12V
  - transmit: 80~450mA @12V (depending on the network condition)
If I'm running off a LiPo bank, the voltage won't be an issue, but drawing 30mA even when idle might be a bit much. Not really a way around it though!

It might be fun to have a LoRa modem as well, as a backup in case I drive somewhere that means I lose signal. That way, so long as I know its rough coordinates, I can drive out and re-establish communications.

## Motion

Treads can be [bought](https://www.aliexpress.com/item/32876365731.html) - they're not *cheap*, but they're not overly expensive. I would probably want to fabricate the main body of the rover in the shop. Plastic < metal, probably? More weatherproof. I keep gravitating towards [this one](https://www.aliexpress.com/item/4000187862847.html) ([build doc](https://gitnova.com/#/Robot/FrameChassis/4WDDampingCar/4WDDampingCar))

I think an RC truck might be the way to go - comes with control electronics I can hopefully hijack, but failing that I can just gut it and hook into the hardware directly. [this](https://uk.banggood.com/Eachine-EAT04-1-or-12-2_4G-4WD-RC-Car-Metal-Body-Shell-Desert-Off-road-Truck-7_4V-1500mAH-RTR-Toy-Black-p-1611391.html?cur_warehouse=CN) looks like s decent one, seems ruged and mostly metal. Will need some waterproofing, but I think that's true of anything I buy. Ideally, I would go a bit bigger so I can fit stuff in a bit more easily, but a lighter chassis might mean longer range. [This is a more plasticy version](https://www.aliexpress.com/item/1005005032547831.html), but I think it might be a little bigger?

I lean towards the tank, since I worry about the load capacity of the cars. 

Read [this](https://blog.ampow.com/rc-brushless-motor-size-chart-choose-the-best/) for help choosing a motor. I think I'll want to be running a 6S battery for lower current draw, but that's gonna call for some step-down stuff to run the compute parts from. For motors, I think I want low-Kv and high voltage, so [these](https://www.aliexpress.com/item/1005001702756074.html) would do great. Plus they're slim, which helps. **Waterproofing**? For an ESC, I think I want to err on the high side of current rating. I think buy [these probably overkill](https://www.aliexpress.com/item/32986228623.html) motors, since I don't know much about the chassis

Probably will want some 5010 750kv motors. They're high torque and slim, but I dunno how weatherproof they'll be.

## Power

If I eyeball total power usage (when active) of the compute parts as about 5W for the raspberry pi, 400mA for the modem to give 3.6W while transmitting, call that 4W, and running two motors at about 30W each, I would guess about 40W total power draw while active. A 20W panel would then need to chage for 2 hours to recover that - if I could charge while driving, that gives me a 50% duty cycle on movement - but remember, you can only charge in the daytime, and a solar panel is unlikely to reach its full charging potential. 

For reference, I can find 20W solar panels on [aliexpress](https://www.aliexpress.com/item/1005004546004726.html) that are specced as `300x145x3MM 20W` and probably around 1kg, so totally doable on the rover. If I splash out and put wings on the thing, I *could* overhang the sides and put two on - but I think it wouldn't be worth it and would be asking for trouble. [Amazon](https://www.amazon.co.uk/Waterproof-Portable-Starter-Monocrystalline-Controller/dp/B0B9T4V3JF/) has [comparable](https://www.amazon.co.uk/Monocrystalline-Waterproof-Maintainer-Motorhomes-Motorcycle/dp/B08QHRWK4M/) things, that are far more likely to be authentic.

From this estimate, I would guess that a relatively standard 4,000mAh LiPo (which typically costs about £100, ouch!) would run the thing for about an hour; (4 Ah * 12V) / 40W = 72 minutes. a 6C motor is aroun £60, here is a [two-pack](https://www.amazon.co.uk/HRB-4000mAh-Battery-Quadcopter-Helicopter/dp/B06XT6L382) on Amazon, or [one 6s](https://www.hobbyrc.co.uk/gnb-4000mah-6s-50c-lipo-battery) on hobbyking.

I should also get something to function as a mini UPS for the controller and modem. That way, I can still communicate with the rover even if I run the main batteries all the way down, which is likely. Especially if there's a run of poor weather. [UPS](https://www.waveshare.com/ups-module-3s.htm)

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

## TODO
- Fix apache
- Write a motor interface - xbox controllers?
- WebRTC LED states?
- WebRTC LED control?



# Setup, prerequisites

Before anything else, 
```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git python3-pip
pip install -U pip
pip install -r requirements.txt
```
And set up the git instance with an SSH key. Then, clone this repo.

## Install `uv4l`
https://www.linux-projects.org/uv4l/installation/

This works on here: http://192.168.1.170:1002/ I have cloned over the web code, it's in `facedetection`. See what you can do with that.

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
sudo apt-get install -y uv4l-webrtc
```


## Start the hardware controller:

The hardware is controlled by its own script. This has to be run with `sudo` priviledges and is interfaced with HTTP, so really shouldn't be exposed to the internet. So, it's only available on localhost, where a middleware API will forward commands to it. It's located in the script [`controller_server.py`](controllers/controller_server.py), and I've written a service configuration that should keep it running. 

First, check the configuration to make sure it will run ok. Then, 
```
sudo cp setup/hardware_controller.service /etc/systemd/system/
sudo systemctl enable hardware_controller
sudo systemctl start hardware_controller
```


## Install and configure Apache2
```
sudo apt-get install -y nginx
```

Really, we should get a proper signed SSL certificate. However, as a stopgap we can get a self-signed one.
To create a new self-signed SSL certificate, with this command:
```
sudo mkdir /etc/nginx/SSL
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/SSL/selfsigned.key -out /etc/nginx/SSL/selfsigned.crt
```
Note that this is not ideal for deployment, but will do for testing.

Then, set up the flask app to be run by nginx. To do this, I have provided a configuration in `setup/rover_server.nginx`. Tweak that, and move it to `/etc/nginx/sites-available/`
```
sudo cp setup/rover.conf /etc/apache2/sites-available/
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
