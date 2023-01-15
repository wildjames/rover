#!/usr/bin/bash

# This script installs the rover controller service
# It should be run as root
cp controller.service /etc/systemd/system/
systemctl enable controller.service
systemctl start controller.service