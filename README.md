# Rover

This will be the playground for my rover control software. I've never done anything like this, so I anticipate learning a lot and making more mistakes than things I get right, but the goal is to get something that is... functional. Self-healing in the case of a crash would be nice as well, but we're gonna have to see about that one.

The rover design goal is to build a remote-controlled vehicle, that is capable of operating in arbitrarily remote enviroments. Obviously, that is limited to places I can signal, so that is limited in reality to places that get mobile internet reception. 

The control software I'm building right now has the following stack:
- Apache2 server
  - handles authentication and URL routing
- Flask app
  - Frontend code, web interface
  - parses JSON input from the operator and publishes commands to be executed to the MQTT host
- Mosquitto MQTT server (local access only?)
  - Brokers communication between the Flask app, and the controllers
- Controller script(s?)
  - Interfaces with the GPIO pins (requires root to do this)
  - Subscribes to the MQTT broker, and executes commands that are published there
  - Publishes the state of the electronics to the MQTT broker



# Notes, TODO

I feel like this is inelegant, especially the MQTT being used to pass messages between python scripts, but I've not come across anything better (yet). In the end, it's likely that I'll delegate the mechanics of the rover to an arduino, likely an ESP32 for the processing speed and threading capability. In that case, I'd probably want to communicate over USB serial, or else screw around with level-shifting the pi 5V signals to ESP32 3.3V signals... But, I think that would allow me to call out to the microcontroller from within the Flask app, and ditch the mosquitto/controller scripts. 

Even with `QoS = 2`, the MQTT interface is unreliable at even moderately high speeds. Might be because I'm testing on a pi Zero? I could drive slowly, but I don't want erroneous inputs! It might be worth using HTTP to communicate - something like [this SO post](https://stackoverflow.com/a/16218248).

Alternatively, I could just try and reconfigure apache to run the flask app as root. I think adding the web user (www?) to the sudoers file. Dunno, food for thought. Though, I don't like the idea of giving the web user root access. I have begun to implement this.

## TODO
- Set up the LED control as a system service, so it starts at boot (and runs as root!)


# Setup, prerequisites


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
Then, set up the flask app to be run by Apache2. To do this, create the file `/etc/apache2/sites-available/rover.conf` with the following contents:
```
<VirtualHost *:80>
        # Add machine's IP address (use ifconfig command)
        ServerName roverpi.local

        # Give an alias to to start your website url with
        WSGIScriptAlias /rover /usr/local/www/rover/rover_app.wsgi

        <Directory /usr/local/www/rover/>
                # set permissions as per apache2.conf file
                Options FollowSymLinks
                AllowOverride None
                Require all granted
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
Then, enable the site with `sudo a2ensite`, and choose `rover` from the list. Then, restart apache2 with `sudo systemctl restart apache2`.

