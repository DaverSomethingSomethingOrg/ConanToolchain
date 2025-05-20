#!/bin/sh

set -xe

# Clean up previous run
#rm -fR src/ build-release/

#conan source --name gcc --version 15.1.0 . 2>&1 | tee CONAN_01_SOURCE.log
conan install --name gcc --version 15.1.0 --profile optPrefix --build=missing . 2>&1 | tee CONAN_02_INSTALL.log
#conan build --name gcc --version 15.1.0 --profile optPrefix . 2>&1 | tee -a CONAN_03_BUILD.log
#conan export-pkg --name gcc --version 15.1.0 --profile optPrefix . 2>&1 | tee CONAN_04_EXPORT-PKG.log

