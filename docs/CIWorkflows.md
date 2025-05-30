# CI Workflows

!!! question "ToDo"

    - Detect new toolchain package definition
      - require approval to *build world*
    - Detect modified toolchain package definition
      - require approval to *build and deploy changes*
    - Platform bootstrap workflow
    - Optional build platform
      
    - SCA built-in or connected
      - Black Duck support
      - dependency_tracker I guess

    - Bootstrap toolchain
    - Build-on-demand workflows
      - single tool-version/platform (+ dependencies)
    - toolchain monorepo skeleton
      - conan recipes

## Basic Operation

### Creating a new Toolchain definition

### Maintaining the Conan Package Index

```none title="Sample Conan Package Index Directory Tree"
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

Deploy packages into a singular *&lt;prefix&gt;* subdirectory within the given
`deployer-folder` directory.

```bash title="Sample Usage"
$ conan install --deployer-folder=nfs_deploy \
                --deployer-package="make/4.4.1" \
                --deployer=nfs_deployer.py \
                --profile=optPrefix \
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
