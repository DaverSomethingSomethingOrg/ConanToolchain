# Sample Usage

## Custom Conan Profile

We add a `install_prefix` option to a custom Conan profile.

```none hl_lines="10-11" title="~/.conan2/profiles/optPrefix"
[settings]
arch=armv8
build_type=Release
compiler=gcc
compiler.cppstd=gnu17
compiler.libcxx=libstdc++11
compiler.version=11
os=Linux

[options]
*:install_prefix=/opt/toolchain
```

## Creating a new Toolchain definition

To connect all of our tool packages together into a single build and
deployment, we create a simple Conan package definition that uses
the `install_prefix` option and lists all primary tools as toplevel
dependencies.  This will help catch any diamond transitive depdendency
version issues early in the process.

```python title="Sample toolchain conanfile.py"
from conan import ConanFile
from conan.tools.layout import basic_layout

class Toolchain(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "install_prefix": [None, "ANY"],
    }
    default_options = {
        "install_prefix": None,
    }

    def requirements(self):

        self.requires("make/4.4.1")
        self.requires("binutils/2.44")
        self.requires("gcc/15.1.0")

        self.requires("clang/19.1.7")
        self.requires("llvm-core/19.1.7")
        self.requires("gtest/1.16.0")
        self.requires("cppunit/1.15.1")

        self.requires("cpython/3.12.7")
        self.requires("nodejs/20.16.0")
        self.requires("openjdk/21.0.2")

        self.requires("cmake/4.0.1")
        self.requires("meson/1.7.2")
        self.requires("ninja/1.12.1")
        self.requires("bazel/7.2.1")

        self.requires("doxygen/1.14.0")


    def layout(self):
        basic_layout(self, src_folder="src")
```

## Running the package builds

```bash title="Sample Usage"
# First seed the Conan Cache by installing all packages, building any
# (or all) that are missing
$ conan install --build=missing .

# Leveraging the seeded cache, run the RPM generator for each package
$ conan install --deployer-folder=rpm_deploy \
                --deployer=rpm_deployer.py \
                --profile=optToolchain \
                .
```

```none title="Sample Directory Tree Output"
rpm_deploy
├── toolchain-gcc-15.1.0
│   └── opt/toolchain
│       ├── bin/make
│       └── share/info/make.info
└── toolchain-gmp-6.3.0
    └── opt/toolchain
        ├── include/gmp.h
        ├── lib/libgmp.a
        └── licenses/COPYING.LESSERv3
```

## NFS toolchain

!!! warning annotate "Unsupported"

    This feature is still under development and probably doesn't work

Deploy packages into a singular *&lt;prefix&gt;* subdirectory within the given
`deployer-folder` directory.

```bash title="Sample Usage"
$ conan install --deployer-folder=nfs_deploy \
                --deployer=nfs_deployer.py \
                --profile=optToolchain \
                .
```

```none title="Sample Directory Tree Output"
nfs_deploy
└── opt
    └── toolchain
        ├── bin
        │   ├── g++-15.1.0
        │   ├── gcc-15.1.0
        │   └── make
        ├── include
        │   ├── c++
        │   │   └── 15.1.0
        │   ├── gmp.h
        │   └── gmpxx.h
        ├── lib
        │   ├── libgmp.a
        │   └── libgmpxx.a
        ├── lib64
        │   └── libgcc_s.so.1
        ├── libexec
        │   └── gcc
        │       └── aarch64-unknown-linux-gnu
        ├── licenses
        │   ├── COPYING.LESSER
        │   ├── COPYING.LESSERv3
        │   ├── COPYINGv2
        │   └── LICENSE
        └── share
            ├── info
            │   └── cpp.info
            └── man
                ├── man1
                └── man7
```
