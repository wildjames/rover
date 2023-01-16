#!/usr/bin/bash

pip install -r ../requirements.txt

# There are some logging files that we will want to create.
# We will create them in the /var/log directory
echo "Creating/cleaning log file directory"
rm -r /home/rover/log
mkdir -p /home/rover/log
chmod -cR 777 /home/rover/log
chgrp -cR adm /home/rover/log


# Create a secret API token to access the rover API
echo $RANDOM | md5sum | head -c 20 > /home/rover/rover_api_token.txt



# TODO: Apache setup should go here. Dockerise that?
echo "Doing Apache2 service check"
systemctl restart apache2.service
echo "Is the Apache2 service running?"
systemctl is-active apache2.service
echo "Is the Apache2 service enabled?"
systemctl is-enabled apache2.service

# This script installs the rover controller service
# It should be run as root
echo "Installing rover controller service"
cp rover_controller.service /etc/systemd/system/
systemctl enable rover_controller.service
echo "Starting rover controller service"
systemctl start rover_controller.service
echo "Is the rover controller service running?"
systemctl is-active rover_controller.service


echo "OK!"