#!/usr/bin/bash

# There are some logging files that we will want to create.
# We will create them in the /var/log directory
mkdir -p /var/log/rover
chmod -R 766 /var/log/rover

# This script installs the rover controller service
# It should be run as root
cp rover_controller.service /etc/systemd/system/
systemctl enable rover_controller.service
systemctl start rover_controller.service
sleep 5
systemctl status rover_controller.service
