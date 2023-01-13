So the basic communication via Flask works ok, and can easily parse out JSON messages. However, to get pin control (which I'll probably need), the process has to be running as root. 
It's probably best to have the Flask portion handle the server stuff, and simply pass the JSON out to another python process that does tha actual GPIO/reaction stuff.
Call them the communicatior, and the controller respectively. For getting data to the controller, `mosquitto` is apparently quite good for interprocess communication.

I will have the Flask interface in the top directory, and keep hardware interfaces in the controller directory.


# Setup, prerequisites


## Install mosquitto:
```
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service
```


## Start the LED controller:
```
sudo python3 controller/led_controller.py
```


## Install python requirements
```
sudo pip3 install -r requirements.txt
```


## Install Apache2
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

