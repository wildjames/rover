#!/usr/bin/bash

# This script installs the rover controller service
# It should be run as root
cp rover_controller.service /etc/systemd/system/
systemctl enable rover_controller.service
systemctl start rover_controller.service
sleep 5
systemctl status rover_controller.service
