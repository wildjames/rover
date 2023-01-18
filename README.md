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

Treads can be [bought](https://www.aliexpress.com/item/32876365731.html) - they're not *cheap*, but they're not overly expensive. I would probably want to fabricate the main body of the rover in the shop. Plastic > metal, probably? More weatherproof

I think an RC truck might be the way to go - comes with control electronics I can hopefully hijack, but failing that I can just gut it and hook into the hardware directly. [this](https://uk.banggood.com/Eachine-EAT04-1-or-12-2_4G-4WD-RC-Car-Metal-Body-Shell-Desert-Off-road-Truck-7_4V-1500mAH-RTR-Toy-Black-p-1611391.html?cur_warehouse=CN) looks like s decent one, seems ruged and mostly metal. Will need some waterproofing, but I think that's true of anything I buy. Ideally, I would go a bit bigger so I can fit stuff in a bit more easily, but a lighter chassis might mean longer range. [This is a more plasticy version](https://www.aliexpress.com/item/1005005032547831.html), but I think it might be a little bigger?

## Power

If I eyeball total power usage (when active) of the compute parts as about 5W for the raspberry pi, 400mA for the modem to give 3.6W while transmitting, call that 4W, and running two motors at about 30W each, I would guess about 40W total power draw while active. A 20W panel would then need to chage for 2 hours to recover that - if I could charge while driving, that gives me a 50% duty cycle on movement - but remember, you can only charge in the daytime, and a solar panel is unlikely to reach its full charging potential. 

For reference, I can find 20W solar panels on [aliexpress](https://www.aliexpress.com/item/1005004546004726.html) that are specced as `300x145x3MM 20W` and probably around 1kg, so totally doable on the rover. If I splash out and put wings on the thing, I *could* overhang the sides and put two on - but I think it wouldn't be worth it and would be asking for trouble. [Amazon](https://www.amazon.co.uk/Waterproof-Portable-Starter-Monocrystalline-Controller/dp/B0B9T4V3JF/) has [comparable](https://www.amazon.co.uk/Monocrystalline-Waterproof-Maintainer-Motorhomes-Motorcycle/dp/B08QHRWK4M/) things, that are far more likely to be authentic.

From this estimate, I would guess that a relatively standard 4,000mAh LiPo (which typically costs about £100, ouch!) would run the thing for about an hour; (4 Ah * 12V) / 40W = 72 minutes.

I should also get something to function as a mini UPS for the controller and modem. That way, I can still communicate with the rover even if I run the main batteries all the way down, which is likely. Especially if there's a run of poor weather.

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
- Write a motor interface
- WebRTC LED states?
- WebRTC LED control?



# Setup, prerequisites

## Install OpenCV
I made a script that follows the instructions from [here](https://pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/). Before you run it though, 
```
sudo nano /etc/dphys-swapfile
```
and set `CONF_SWAPSIZE=2048`. The default is 100. Then, restart the service with `sudo /etc/init.d/dphys-swapfile restart`.

Then, run the script from your home directory. This is a permission thing.
```
cd ~
sudo path_to_rover/setup/install_opencv.sh
```

## Install `uv4l`
https://www.linux-projects.org/uv4l/installation/

This works on here: http://192.168.1.170:1002/ I have cloned over the web code, it's in `facedetection`. See what you can do with that.

I think 

## Start the LED controller:
```
sudo python3 controller/led_controller.py
```


## Install python requirements
```

sudo pip3 install -r requirements.txt
```


## Install and configure Apache2
```
sudo apt-get install -y apache2
```
We want HTTPS, so install the related plugin
```
sudo a2enmod ssl
```

Really, we should get a proper signed SSL certificate. However, as a stopgap we can get a self-signed one.
To create a new self-signed SSL certificate, with this command:
```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt
```
Note that this is not ideal for deployment, but will do for testing.

Then, set up the flask app to be run by Apache2. To do this, I have provided a configuration in `setup/rover.conf`. Tweak that, and move it to `/etc/apache2/sites-available/`
```
sudo cp setup/rover.conf /etc/apache2/sites-available/
```
Then, enable the site with `sudo a2ensite`, and choose `rover` from the list. Then, restart apache2 with `sudo systemctl restart apache2`.

