# Demo - MultiPhase Toolchain Build

We use our tools to build our tools.  But we need to get started
on a new platform by building our basic compiler suite.

Using caching in GitHub Actions, we can connect multiple toolchain
workflows to each other, so that dependencies built in one phase
can be installed for use in subsequent phases.

### Phase 1 - GNU binutils

GCC depends on binutils, so that's where we start.  We need a working
compiler to build our tools though, so we'll use a special bootstrap
container image with the OS Vendor's compiler chain installed.

```python title="phase 1 - conanfile.py"
    # For this bootstrapping phase we'll depend on OS vendor-provided tools
    def system_requirements(self):
        Apt(self).install(["make", "cmake", "binutils", "gcc"])
        Yum(self).install(["make", "cmake", "binutils", "gcc"])

    def requirements(self):
        self.requires("binutils/2.42")
```

### Phase 2 - bootstrapping CMake, GNU Make, and GCC

In Phase 2, we'll build our GCC configured to use our binutils package from
Phase 1.  We're still depending on the system GCC however, so we still want
the OS Vendor's binutils available for their GCC as well.

```python title="phase 2 - conanfile.py"
    # For this bootstrapping phase we'll depend on OS vendor-provided tools
    def system_requirements(self):
        Apt(self).install(["make", "cmake", "binutils", "gcc",
                           "opt+toolchain-binutils_2.42-1",
                          ])
        Yum(self).install(["make", "cmake", "binutils", "gcc",
                           "opt_toolchain-binutils-2.42-1",
                          ])

    def requirements(self):
        self.requires("make/4.4.1")
        self.requires("cmake/4.0.1")
        self.requires("gcc/12.2.0"
```

### Phase 3 - Clean rebuilds using our toolchain

Finally, we will go back to our OS-minimal container image, install the
tools we built in the previous phases, and rebuild all of our tools.

By using the OS-minimal image this time, we can be certain that there
will be no surprise dependencies at all on the original OS Vendor toolchain.

We only upload these final builds to Artifact Management, along with a brand
new Conan Build container image for building all other tools we support.
The previous packages built with our bootstrap image are discarded.

```python title="phase 3 - conanfile.py"
    # Finally, we use our tools from phase 1 and 2 to build our tools again
    def system_requirements(self):
        Apt(self).install(["opt+toolchain-make-4.4.1-1",
                           "opt+toolchain-cmake-4.0.1-1",
                           "opt+toolchain-gcc-12.2.0-1",
                           "opt+toolchain-binutils_2.42-1",
                          ])
        Yum(self).install(["opt_toolchain-make-4.4.1-1",
                           "opt_toolchain-cmake-4.0.1-1",
                           "opt_toolchain-gcc-12.2.0-1",
                           "opt_toolchain-binutils-2.42-1",
                          ])

    def requirements(self):
        self.requires("make/4.4.1")
        self.requires("cmake/4.0.1")
        self.requires("binutils/2.42")
        self.requires("gcc/12.2.0"
```

!!! note annotate "For each platform, we end up with an overall flow that looks like this"

    ![Conan Toolchain Demo](img/conan_toolchain_demo.png)

#### See Also

!!! github-reference annotate "[conan-docker-tools](https://github.com/conan-io/conan-docker-tools)"

    The Conan project builds similar images for this purpose, but with a
    few significant differences:

    - We use the same Conan recipes and mechanism (conan) to build our
      build container toolchain that we provide to developers.
    - We build both Ubuntu and AlmaLinux (RedHat compatible), as well as
      ARM and x86 CPU architectures.
