#!/bin/bash

#    Author: Qian, Ryan
#    Date: 21-Sep-2012
#    eMail: ryan.qian@gmail.com
#
#   This is the postinstall script after Solaris 11 installation.
#   For install bunch of esential packages and some basic configuration

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

gatherinfo (){
    hostname=$(hostname)
    ipstring=$(ipadm show-addr|grep ok |egrep -v "lo0|:"  |awk '{print $4}')
    ipaddr=$(echo $ipstring|awk -F/ '{print $1}') 
    netmaskbit=$(echo $ipstring|awk -F/ '{print $2}')
    echo "IP Address: " $ipaddr
    echo "Netmask Bits: " $netmaskbit
}

gatherinfo

# Stop GDM
if ask "Do you want to Disable GDM (Graphic Login) ?";then
    sudo svcadm disable gdm
fi

# install 
echo "###############################"
echo "Install essential Packages, also some of Opencsw packages.... "
echo "###############################"
sudo pkg update
sudo pkg install lftp autoconf unrar setuptools-26 system/header cvs developer/versioning/subversion git
sudo pkg install -v \
 pkg:/data/docbook \
 pkg:/developer/astdev \
 pkg:/developer/build/make \
 pkg:/developer/build/onbld \
 pkg:/developer/illumos-gcc \
 pkg:/developer/gnu-binutils \
 pkg:/developer/opensolaris/osnet \
 pkg:/developer/java/jdk \
 pkg:/developer/lexer/flex \
 pkg:/developer/object-file \
 pkg:/developer/parser/bison \
 pkg:/developer/versioning/mercurial \
 pkg:/library/glib2 \
 pkg:/library/libxml2 \
 pkg:/library/libxslt \
 pkg:/library/nspr/header-nspr \
 pkg:/library/perl-5/xml-parser \
 pkg:/library/security/trousers \
 pkg:/print/cups \
 pkg:/print/filter/ghostscript \
 pkg:/runtime/perl-510 \
 pkg:/runtime/perl-510/extra \
 pkg:/runtime/perl-510/module/sun-solaris \
 pkg:/system/library/math/header-math \
 pkg:/system/library/install \
 pkg:/system/library/dbus \
 pkg:/system/library/libdbus \
 pkg:/system/library/libdbus-glib \
 pkg:/system/library/mozilla-nss/header-nss \
 pkg:/system/header \
 pkg:/system/management/product-registry \
 pkg:/system/management/snmp/net-snmp \
 pkg:/text/gnu-gettext \
 pkg:/library/python-2/python-extra-24 \
 pkg:/web/server/apache-13

cd ~; git clone https://github.com/rmrf/BashEnv.git
mv ~/.bash_profile ~/.bash_profleBAK
ln -s ~/BashEnv/sol11_bash_profile ~/.bash_profile



# install sun studio12u1
sudo pkg set-publisher -g http://pkg.openindiana.org/legacy opensolaris.org
sudo pkg install pkg:/developer/sunstudio12u1
sudo mkdir -p /opt/SUNWspro
sudo ln -s /opt/sunstudio12.1 /opt/SUNWspro/sunstudio12.1

# Grant root login
# Change root from role to normal user, Security?! I know.. I know...
echo "###############################"
echo "Modify some configuration files to grant root login......"
echo "###############################"
sudo perl  -pi -e 's/^root::::type=role$/root::::type=normal/'  /tmp/user_attr
sudo perl  -pi -e 's/^PermitRootLogin.*$/PermitRootLogin yes/' /etc/ssh/sshd_config

sudo svcadm restart ssh


# install gmp from source,  pycrypto can't be install without this step.
echo "###############################"
echo "Install gmp 5.0.5 from source......"
echo "###############################"
cd /tmp
wget -c ftp://ftp.gnu.org/gnu/gmp/gmp-5.0.5.tar.bz2
gtar -xzvf gmp-5.0.5.tar.bz2
cd gmp-5.0.5;./configure;make;sudo make install


# install PIP
echo "###############################"
echo "Install pip 1.2.1"
echo "###############################"
cd /tmp
wget -O pip-1.2.1.tar.gz -c "http://pypi.python.org/packages/source/p/pip/pip-1.2.1.tar.gz#md5=db8a6d8a4564d3dc7f337ebed67b1a85" 
cd pip-1.2.1
python setup.py install

