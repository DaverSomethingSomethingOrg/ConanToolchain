# Toolchain Build System using Conan

[Click here to view the published version of this documentation with more details](https://daversomethingsomethingorg.github.io/ConanToolchain/)

Maintaining a multi-platform, 3rdParty toolchain ecosystem consistent
for all developers offers some significant challenges.

The goal of this project is to provide a comprehensive, reliable system
to build a toolchain that works by design.  Configured, built, and installed
consistently.  Rather than trying to manipulate tools to work in
configurations they were not originally built for.

To achieve this we leverage the [Conan C/C++ package manager](https://conan.io)
to produce repeatable builds using consistent host configutations.
Delivering a complete toolchain in the form of OS System packages for Linux.

To put this all together, I've developed these integration pieces:

- https://github.com/DaverSomethingSomethingOrg/conan-system-packaging

   RPM and .deb package generation using Conan.  `conan-system-packaging`
   provides `rpm_deployer` and `deb_deployer` custom deployers.

- https://github.com/DaverSomethingSomethingOrg/conan-github-workflows

    Custom GitHub Actions Reusable Workflows
    to provide multi-platform build/test/release workflows for individual
    Conan builds, and for complete toolchain builds.

- https://github.com/DaverSomethingSomethingOrg/conan-build-container

    Custom Docker container images for building Conan packages.

By delivering OS packages, we are able to:

- Provide the simplest, easiest tool installation for Developers.
  Especially for custom Container images
- Link to any vendor-provided OS dependencies so that `yum install -y <tool>`
  or `apt-get install -y <tool>` "just works"
- Register our tool component packages with Software Composition
  Analysis (SCA) tools like
  [Black Duck SCA](https://www.blackduck.com/software-composition-analysis-tools/black-duck-sca.html)
  or [Dependency-Track](https://dependencytrack.org/)
- Provide an end-to-end auditable software supply chain

If you are using your own compiler/interpreter versions, or special ABI
configurations for your products, then you will likely want your
toolchains to be built using configurations consistent and compatible with
your products.

[Click here to view the published version of this documentation with more details](https://daversomethingsomethingorg.github.io/ConanToolchain/)

## License and Copyright

Copyright © 2025 David L. Armstrong

[Apache-2.0](LICENSE.txt)
