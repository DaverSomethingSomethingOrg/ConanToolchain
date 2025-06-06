# Toolchain Build System using Conan

Maintaining a multi-platform, 3rdParty toolchain ecosystem consistent
for all developers offers some significant challenges.  With the right
technologies working together however, these challenges can be overcome.

The goal of this project is to provide a comprehensive, reliable system
to build a toolchain that works by design, rather than trying to hack
or manipulate tools to work in configurations they were not originally
built for.

This project consists primarily of a fairly simple (but critical) custom
deployer for the [Conan C/C++ package manager](https://conan.io).  This
deployer allows us to deliver a complete toolchain, built using consistent
host configurations, and delivered in the form of RPM packages for Linux.
(Debian .deb packaging coming soon..)

By delivering RPM packages, we are able to:

- Provide the simplest, easiest tool installation for Developers,
  especially for custom Container images
- Link to any RedHat-provided OS dependencies so `yum install -y <tool>`
  "just works".
- Register our component packages with Software Composition Analysis (SCA)
  tools like Black Duck
- Provide an end-to-end auditable software supply chain

If you are using your own compiler versions, or ABI configurations for
your products, then you will likely want your toolchains to be built
using configurations consistent and compatible with your products.

## Why is installation prefix important?

While a great deal of software is written in relocatable form these days,
there is still a long way to go.  Tools such as GCC need to be able to
locate it's libraries, as well as tools like `as` and `ld` from a different
package (binutils).  Relying on `$PATH` or `$ORIGIN` may not be sufficient
to locate the right ones.

For more in-depth discussion of the issues in maintaining an Enterprise
Engineering Development toolchain, and the benefits of this solution,
read on..

- [But Why?](docs/ButWhy.md)
- [Sample Usage](docs/SampleUsage.md)
- [Conan Setup and Recipe Pre-requisites](docs/ConanRecipePreReqs.md)
