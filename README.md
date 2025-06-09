# Toolchain Build System using Conan

Maintaining a multi-platform, 3rdParty toolchain ecosystem consistent
for all developers offers some significant challenges.

The goal of this project is to provide a comprehensive, reliable system
to build a toolchain that works by design.  Configured built, and installed
consistently, rather than trying to manipulate tools to work in
configurations they were not originally built for.

This project consists primarily of a fairly simple (but critical) custom
deployer for the [Conan C/C++ package manager](https://conan.io).  This
deployer allows us to deliver a complete toolchain, built using consistent
host configurations, and delivered in the form of OS packages for Linux.
Today we have an RPM package deployer, with a Debian .deb package deployer
coming soon.

By delivering OS packages, we are able to:

- Provide the simplest, easiest tool installation for Developers,
  especially for custom Container images
- Link to any vendor-provided OS dependencies so `yum install -y <tool>`
  or `apt-get install -y <tool>` "just works".
- Register our tool component packages with Software Composition
  Analysis (SCA) tools like
  [Black Duck SCA](https://www.blackduck.com/software-composition-analysis-tools/black-duck-sca.html)
  or [Dependency-Track](https://dependencytrack.org/)
- Provide an end-to-end auditable software supply chain

If you are using your own compiler/interpreter versions, or special ABI
configurations for your products, then you will likely want your
toolchains to be built using configurations consistent and compatible with
your products.

## Why is installation prefix important?

A great deal of software is written in relocatable form these days, but
there is still a long way to go.  Tools such as GCC need to be able to
locate it's own libraries, as well as tools like `as` and `ld` from a
different package (binutils).  Relying on `$PATH` or `$ORIGIN` may not
be sufficient to consistently and reliably locate the correct ones.

For more in-depth discussion of the issues in maintaining an Enterprise
Engineering Development toolchain, and the benefits of this solution,
read on..

- [But Why?](docs/ButWhy.md)
- [Sample Usage](docs/SampleUsage.md)
- [Conan Setup and Recipe Pre-requisites](docs/ConanRecipePreReqs.md)
