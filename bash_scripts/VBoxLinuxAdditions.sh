#!/bin/bash

# This script mounts the VirutalBox Linux Additions and installs them
echo "Do you want to install the Virutal Machine Guest Additions, and "
echo -n "did you Insert the Guest Additions CD? (Devices--Insert Guest Additions CD image)... (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Continuing..."
    echo "Running apt-get for virtualbox requirements"
    sudo apt install build-essential dkms -y
    echo "Mounting CD-ROM drive and running VBoxLinuxAdditions:"
    sudo mount /dev/cdrom /media/cdrom
    sudo /media/cdrom/VBoxLinuxAdditions.run
else
    echo "Aborting, Virtual Machine Guest Additions..."
fi

