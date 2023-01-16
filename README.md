# Rover

This will be the playground for my rover control software. I've never done anything like this, so I anticipate learning a lot and making more mistakes than things I get right, but the goal is to get something that is... functional. Self-healing in the case of a crash would be nice as well, but we're gonna have to see about that one.

The rover design goal is to build a remote-controlled vehicle, that is capable of operating in arbitrarily remote enviroments. Obviously, that is limited to places I can signal, so that is limited in reality to places that get mobile internet reception. 

The control software I'm building right now has the following stack:
- Apache2 server
  - handles authentication and URL routing
- Flask app
  - Frontend code, web interface
  - parses JSON input from the operator and passes commands to be executed to the hardware controller
- Hardware controller script(s?)
  - Interfaces with the GPIO pins (requires root to do this)
  - runs its own HTTP server, with its own API. This, however, runs as root so is not publicly accessible.



# Notes, TODO

Software interface works, and has authenication needed to hit the endpoints. An API token is generated, and has to be given in the `Auithorization` html header. Next stop: Hardware.
Will I end up writing an app to control this? It's either that or the browser... And that would probably take JavaScript?

## TODO
- Write a motor interface
- Need to get camera feed somehow


# Setup, prerequisites

## Install OpenCV
I made a script that follows the instructions from [here](https://pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/). Before you run it though, 
```
sudo nano /etc/dphys-swapfile
```
and set `CONF_SWAPSIZE=2048`. The default is 100. Then, restart the service with `sudo /etc/init.d/dphys-swapfile restart`.

Then,
```
cd setup
sudo ./install_opencv.sh
```

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

