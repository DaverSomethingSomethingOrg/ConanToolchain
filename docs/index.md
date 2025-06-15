# Toolchain Build System using Conan

Maintaining a multi-platform, 3rdParty toolchain ecosystem consistent
for all developers offers some significant challenges.

The goal of this project is to provide a comprehensive, reliable system
to build a toolchain that works by design.  Configured built, and installed
consistently, rather than trying to manipulate tools to work in
configurations they were not originally built for.

To achieve this we leverage the [Conan C/C++ package manager](https://conan.io)
to produce repeatable builds using consistent host configutations,
delivering a complete toolchain in the form of OS packages for Linux.

To put this all together, I've developed some integration pieces:

!!! github-reference annotate "[conan-system-packaging](https://github.com/DaverSomethingSomethingOrg/conan-system-packaging)"

    RPM and .deb package generation using Conan.  `conan-system-packaging`
    provides `rpm_deployer` and `deb_deployer`
    [custom deployers](https://docs.conan.io/2/reference/extensions/deployers.html)
    
    - https://github.com/DaverSomethingSomethingOrg/conan-system-packaging

!!! github-reference annotate "[conan-github-workflows](https://github.com/DaverSomethingSomethingOrg/conan-github-workflows)"

    Custom [GitHub Actions Reusable Workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows)
    to provide multi-platform build/test/release workflows for individual
    Conan builds, and for complete toolchain builds.

    - https://github.com/DaverSomethingSomethingOrg/conan-github-workflows

!!! docker-reference annotate "[conan-build-container](https://github.com/DaverSomethingSomethingOrg/conan-build-container)"

    Custom Docker container images for building Conan packages.

    - https://github.com/DaverSomethingSomethingOrg/conan-build-container

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

- [But Why?](ButWhy.md)
- [Sample Usage](SampleUsage.md)
- [Conan Setup and Recipe Pre-requisites](ConanRecipePreReqs.md)

## License and Copyright

Copyright © 2025 David L. Armstrong

[Apache-2.0](LICENSE.txt)
