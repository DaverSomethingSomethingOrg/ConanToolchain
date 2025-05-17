# Conan Toolchain Build System

## Introduction

- Consistently documented configuration for all tool versions across
  all supported platforms
- Package Dependency Integration with OS/minimal base image
- Accommodate custom environment or dependency version requirements
  indepent of OS
- Conan is not intended to support non-relocatable tools out of the box.
- Integrity validated end-to-end
  - Source tarball sha is checked prior to unpacking
  - Conan provides built-in integrity validation for packages
    - `conan cache check-integrity <pattern>`
  - Custom deployer tool generates signed packages using OS tools

### What is this

- Conan tweaks and enhancements to support building and deploying tools
  to a set prefix, including non-relocatable tools.

### Where things get weird

We completely diverge from standard Conan behavior where dependencies
are concerned.  For these toolchain builds we disable the defined
Conan dependencies and replace them by installing prebuilt toolchain
RPMs.

We make sure to install dependency RPMs to use as
dependency for tools higher in the chain.

It's important that the resulting toolchain deployment be entirely
self-sufficient with no dependencies on anything outside of the toolchain
or provided explicitly through OS dependencies (/usr, /lib)

!!! warning annotate "Warning"

    The Conan authors discourage use of Conan for this purpose, but Conan
    is the only tool that can provide strong consistency and runtime link
    compatibility between developer toolchain, runtime depdendencies, and
    containerized runtime environment (or NFS automounted repository).

    Conan Deployer Best Practices (see Note at bottom):

    - https://docs.conan.io/2/examples/extensions/deployers/dev/development_deploy.html

#### Toolchain `make` vs. OS `make` packages

Package managers like RPM only allow a single version of a given package
&lt;name&gt; to be installed.  In order to support RPM installation, we
need to use different package names than the OS packages.

To this end we apply a `toolchain-` prefix to the name of each tool, like
`toolchain-make-4.4.1`.  This allows us to keep the version string original,
and still keep the original tool name embedded.

!!! question "ToDo"

    - Make the RPM package prefix configurable
