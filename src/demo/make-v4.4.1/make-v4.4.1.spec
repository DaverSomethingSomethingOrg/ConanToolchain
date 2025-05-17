Name:           toolchain-make
Version:        4.4.1
Release:        1%{?dist}
Summary:        A GNU tool which simplifies the build process for users
BuildArch:      aarch64

License:        GPLv3+
Source0:        %{name}-%{version}.tar.gz

#Vendor:
#Packager:

# We do NOT want automatic dependency detection
AutoReqProv:    no
#Requires:       bash

%description
GNU Make is a tool which controls the generation of executables and other non-source files of a program from the program's source files

%prep
%setup -q

%install
cp -pR * $RPM_BUILD_ROOT

#%clean
#rm -rf $RPM_BUILD_ROOT

%files
/opt/daver
