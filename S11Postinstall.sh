#!/bin/bash

#    Author: Qian, Ryan
#    Date: 21-Sep-2012
#    eMail: ryan.qian@gmail.com
#
#   This is the postinstall script after Solaris 11 installation.
#   For install bunch of esential packages

ask () {
   echo $1
   echo -n "Continue (y/n)? "
   read ans
   case $ans in
    y | Y ) 
       return 0
        ;;
    * ) echo
        return 1
        ;;
   esac
}


# Stop GDM
if ask "Do you want to Disable GDM (Graphic Login) ?";then
    sudo svcadm disable gdm
fi

# install 
echo "Install Packages..... "
sudo pkg install autoconf gcc-45 unrar setuptools-26
