# `rpm_deployer.py` - Conan Custom Deployer

- Iterate through the dependency graph
  - copy the package contents of each dependency into a tree rpmbuild can use
  - tar up the tree, making sure the prefix appears from the root directory
- Call Into [RPM / .deb Package Generation](#rpm-deb-package-generation)
  - Label/Name the package
  - Use the new tarball as the source files
  - Fill in all of the RPM metadata using `conanfile.py` details.

!!! note annotate "Reference"

    - https://github.com/conan-io/conan-extensions/blob/main/extensions/deployers/
    - https://docs.conan.io/2/reference/extensions/deployers.html#reference-extensions-deployers
    - https://docs.conan.io/2/examples/extensions/deployers/dev/development_deploy.html#examples-extensions-builtin-deployers-development
    - https://github.com/bkircher/python-rpm-spec

## Python Toolchain Builder Wrapper

- Orchestrate Conan API directly to inspect `conanfile.py` dependencies
- verify dependencies are installed/exist as RPMs
- connect dependency RPMs to spec file
- manage independent deploy folders for each toolversion?  conandata.yml?

!!! question "Questions and Ideas"

    - leverage conancenter package definitions when available
    - build to our custom profiles
    - `conan install --deployer-folder`
      - `deploy_folder` as part of profile?
      - look at `full_deploy`, `direct_deploy`, `runtime_deploy`
      - `direct_deploy` - create a metapackage for the toolchain path with all package versions specified?
        - what about missing transitive dependencies?  Are they allowed from outside our own source and SCA?
    - `conandata.yml` file for install prefix?
    - `conanfile.py` passing prefix to `AutotoolsToolchain.configure_args`
      - Use `self.deploy_folder`?
      - Runtime dependencies need to be built and installed similarly

!!! note annotate "Reference"

    - https://docs.conan.io/2/reference/conanfile/methods/deploy.html
    - https://github.com/conan-io/conan-center-index/blob/master/recipes/gcc/all/conanfile.py
