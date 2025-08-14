# Toolchain Build System using Conan

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

!!! github-reference annotate "[conan-toolchain-demo](https://github.com/DaverSomethingSomethingOrg/conan-toolchain-demo)"

    Example Usage of the `conan-github-workflows` for practical scenarios.
    Starting with the gcc/binutils/make/cmake toolchain installed into our
    `conan-build-container`.

    Documented in [Demo - MultiPhase Toolchain Build](DemoMultiPhase.md)

!!! docker-reference annotate "[conan-build-container](https://github.com/DaverSomethingSomethingOrg/conan-build-container)"

    Custom Docker container images for building Conan packages.

    These images provide basic conan functionality and GCC toolchain
    from OS Vendor provided packages:

    - `conan-base-${os_name}:${arch}-latest`
    - `conan-bootstrap-${os_name}:${arch}-latest`
    
    And these add our own Conan GCC Toolchain and other useful toolchain
    construction tools onto the base image.

    - `conan-build-${os_name}:${arch}-latest`
    - `conan-docker-build-${os_name}:${arch}-latest`

    OS/Platform support includes:
    
    - AlmaLinux 9.6 (x86_64, aarch64)
    - Ubuntu 24.04LTS (x86_64, aarch64)

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

For more in-depth discussion of the issues in maintaining an Enterprise
Engineering Development toolchain, and the benefits of this solution,
read on..

## License and Copyright

Copyright © 2025 David L. Armstrong

[Apache-2.0](LICENSE.txt)
