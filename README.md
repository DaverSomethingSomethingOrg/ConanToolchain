# Conan Toolchain Build System

## Introduction

This is both extremely straightforward and also complicated at the same
time.

Every example I've seen to date requires dependening on some simplifying
assumptions that rely on well-behaved software builds.  In my experience
this does not lead to a reliable result.

In my experience, the most straightforward and reliable mechanism is to
directly leverage the existing mechanisms that will be used in production
anyway.

If we are generating a series of RPMs for each package in our toolchain,
then those same RPMs should satisfy the role of our dependencies at
build time also.  Many of these RPMs will be build dependencies for
other RPMs, not necessarily just runtime.

### My approach

1. Support `prefix` option in all `conanfile.py`

   ```python
   tc = None
   if self.options.prefix:
      tc = AutotoolsToolchain(self, prefix=self.options.prefix)
   else:
      tc = AutotoolsToolchain(self)
   ```

1. Replace Conan depedencies with prefixed RPM dependencies

   Make sure they are installed prior to the build.  3rdParty builds can
   do funny things when dependencies are missing.

   ```python
   def requirements(self):
      if self.options.prefix:
          yum = package_manager.Yum(self)
          yum.install([f"{ prefix }-mpc-1.2.0"], update=True, check=True)
      else:
          self.requires("mpc/1.2.0")
   ```

1. Conan custom deployer builds RPMs and installs them in dependency order.


### `system_requirements`

The packages we are building are generally not interchangeable with other
system provided packages, so we're not interested in taking "just any"
system package.  We explicitely want the packages we generate ourselves.

### `patchelf`

- https://github.com/conan-io/conan/issues/2660
- https://enchildfone.wordpress.com/2010/03/23/a-description-of-rpath-origin-ld_library_path-and-portable-linux-binaries/

This works for locating libraries, but what else?

gcc hardcodes the path to `as` and `ld`, and Python locating it's
installed modules.  3rdParty tools make themselves non-relocatable for
many reasons and in many different ways we cannot fathom.  We cannot
make such assumptions.

String length is also an issue.  What if you're desired prefix is really long?
The example works because "XORIGIN" and "$ORIGIN" are the same length string.
How do we accommodate long strings for `patchelf` to insert?  How long is
enough?

Wait.. we're here trying to modify something already done and working, not
build it to work by design...

Here's one example where we end up with the original dependency paths get
attached to a build in ways that cannot easily be detected and patched
automatically:

```bash
[root@771677d358c1 aarch64]# /opt/toolchain/bin/gcc-15.1.0 -v
Using built-in specs.
COLLECT_GCC=/opt/toolchain/bin/gcc-15.1.0
COLLECT_LTO_WRAPPER=/opt/toolchain/libexec/gcc/aarch64-unknown-linux-gnu/15.1.0/lto-wrapper
Target: aarch64-unknown-linux-gnu
Configured with: /tmp/gcc/gcc-v15.1.0/src/configure --prefix=/opt/toolchain --bindir='/opt/toolchain/bin' --sbindir='/opt/toolchain/bin' --libdir='/opt/toolchain/lib' --includedir='/opt/toolchain/include' --oldincludedir='/opt/toolchain/include' --enable-languages=c,c++,fortran --disable-nls --disable-multilib --disable-bootstrap --with-pkgversion='conan GCC 15.1.0' --program-suffix=-15.1.0 --with-bugurl=https://github.com/conan-io/conan-center-index/issues --with-zlib=/root/.conan2/p/b/zlib4f3877b444fa4/p --with-isl=/root/.conan2/p/b/isl59366a6d529b1/p --with-gmp=/root/.conan2/p/b/gmpcc5fb91b1428b/p --with-mpc=/root/.conan2/p/b/mpc66365fb0210d9/p --with-mpfr=/root/.conan2/p/b/mpfr067752b1b16f6/p
Thread model: posix
Supported LTO compression algorithms: zlib
gcc version 15.1.0 (conan GCC 15.1.0) 
[root@771677d358c1 aarch64]# 
```

### Virtual Environment

No absolute paths available without `chroot`

- https://github.com/conan-io/conan/issues/3280
  - "We want to define the destination directory at consumption-time, not package-time."
    - Won't work for non-relocatable tools.
- https://github.com/conan-io/conan/issues/7432
- https://github.com/conan-io/conan/issues/3243
- https://github.com/conan-io/conan/issues/2660#issuecomment-406557370
- https://github.com/conan-io/conan/issues/5664
- https://github.com/conan-io/conan/issues/11686

- https://github.com/conan-io/conan/issues/3541#issuecomment-420949405

- No support for multiple versions (distinct prefixes per tool).
  - It's easy enough to deploy, but gets more complicated at build time,
    locating each dependency prefix for connecting RPATH, etc.


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

- Source is downloaded, stored as original artifact
  - Signed commit in git or generic package in Artifactory
  - Source may be patched, but not changed.  Patches need to be checksum'd too
  - Build Configuration changes are patch releases also
- Packaged into Conan for C/C++ product integration
  - Python for AI Apps, shared library dependencies
  - Conan provides source and binary integrity validation on every install
- Packaged into RPMs for devcontainers, CI containers, production release containers
  - RPM provides connection from container image to original source
- Software Composition Analysis gets a record of each.
  - Original Source Component tarball
    - Where did it come from
    - Original signature/checksum
  - Signed RH* Conatainer image records all installed packages `rpm -qa`
  - Signed RPM package records original source package 
- Conan provides dependency graph
  - We can easily traverse the tree, `build world` in order of dependency resolution
    - Or specify pattern[s] of packages to install (with dependencies)
  - Conan will even build any missing (not already pre-built) dependencies and package them up too


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
