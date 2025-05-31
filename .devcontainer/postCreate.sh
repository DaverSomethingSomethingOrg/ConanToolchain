#!/bin/bash

# Official `python` image is Debian based.
# apt-get update
# apt-get install build-essential devscripts fakeroot

# For RH* support we use AlmaLinux
# VS Code requires git so we do that in Dockerfile before we get here
#yum install -y git
yum install --enablerepo crb -y \
    tree \
    python3-pip \
    binutils \
    gcc \
    gcc-c++ \
    libstdc++-static \
    make \
    cmake \
    wget \
    rpmdevtools \
    rpmlint \
    perl-File-Compare \
    perl-FindBin \
    perl-IPC-Cmd \
    perl-Digest-SHA \
    perl-threads \
    perl-Thread-Queue \
    perl-open \
    texinfo

pip install --no-cache-dir -r requirements.txt

# Initialize Conan settings
#TODO git clone our Conan Confg repo here I guess?
conan profile detect