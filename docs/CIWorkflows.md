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
