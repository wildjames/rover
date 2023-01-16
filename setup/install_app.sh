#!/usr/bin/bash

python3 -m pip install -r ../requirements.txt

# There are some logging files that we will want to create.
# We will create them in the /var/log directory
echo "Creating/cleaning log file directory"
rm -r /home/rover/log
mkdir -p /home/rover/log
chmod -cR 777 /home/rover/log
chgrp -cR adm /home/rover/log


# Create a secret API token to access the rover API
echo $RANDOM | md5sum | head -c 20 > /home/rover/rover_api_token.txt

apt install libwayland-cursor0 libxfixes3 libva2 \
    libdav1d4 libavutil56 libxcb-render0 libwavpack1 \
    libvorbis0a libx264-160 libx265-192 libaec0 libxinerama1 \
    libva-x11-2 libpixman-1-0 libwayland-egl1 libzvbi0 \
    libxkbcommon0 libnorm1 libatk-bridge2.0-0 libmp3lame0 \
    libxcb-shm0 libspeex1 libwebpmux3 libatlas3-base \
    libpangoft2-1.0-0 libogg0 libgraphite2-3 libsoxr0 \
    libatspi2.0-0 libdatrie1 libswscale5 librabbitmq4 \
    libhdf5-103-1 libharfbuzz0b libbluray2 libwayland-client0 \
    libaom0 ocl-icd-libopencl1 libsrt1.4-gnutls libopus0 \
    libxvidcore4 libzmq5 libgsm1 libsodium23 libxcursor1 \
    libvpx6 libavformat58 libswresample3 libgdk-pixbuf-2.0-0 \
    libilmbase25 libssh-gcrypt-4 libopenexr25 libxdamage1 \
    libsnappy1v5 libsz2 libdrm2 libxcomposite1 libgtk-3-0 \
    libepoxy0 libgfortran5 libvorbisenc2 libopenmpt0 libvdpau1 \
    libchromaprint1 libpgm-5.3-0 libcairo-gobject2 libavcodec58 \
    libxrender1 libgme0 libpango-1.0-0 libtwolame0 libcairo2 \
    libatk1.0-0 libxrandr2 librsvg2-2 libopenjp2-7 \
    libpangocairo-1.0-0 libshine3 libxi6 libvorbisfile3 \
    libcodec2-0.9 libmpg123-0 libthai0 libudfread0 libva-drm2 \
    libtheora0 -y
apt-get install python3-h5py -y

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