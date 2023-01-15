#!/usr/bin/bash

# There are some logging files that we will want to create.
# We will create them in the /var/log directory
echo "Creating log file directory"
mkdir -p /var/log/rover
chgrp -R adm /var/log/rover
chmod -R 666 /var/log/rover


# TODO: Apache setup should go here. Dockerise that?
echo "Doing Apache2 service check"
systemctl restart apache2.service
systemctl status apache2.service


# This script installs the rover controller service
# It should be run as root
echo "Installing rover controller service"
cp rover_controller.service /etc/systemd/system/
systemctl enable rover_controller.service
echo "Starting rover controller service"
systemctl start rover_controller.service
sleep 5
systemctl status rover_controller.service


echo "OK!"