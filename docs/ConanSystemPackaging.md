# Conan System Packaging - Custom Deployers

!!! github-reference annotate "[conan-system-packaging](https://github.com/DaverSomethingSomethingOrg/conan-system-packaging)"

    RPM and .deb package generation using Conan.  `conan-system-packaging`
    provides `rpm_deployer` and `deb_deployer`
    [custom deployers](https://docs.conan.io/2/reference/extensions/deployers.html)

    - https://github.com/DaverSomethingSomethingOrg/conan-system-packaging

- Iterate through the dependency graph
  - copy the package contents of each dependency into a tree rpmbuild can use
  - tar up the tree, making sure the prefix appears from the root directory
- Call Into [RPM / .deb Package Generation](#rpm-deb-package-generation)
  - Label/Name the package
  - Use the new tarball as the source files
  - Fill in all of the RPM metadata using `conanfile.py` details.
  - Translating Conan dependencies into RPM dependencies is important for ease-of-use in Container builds
    - `yum install -y toolchain-gcc` should produce an end-result that "just works" without missing dependencies.

!!! note annotate "Reference"

    - https://john-tucker.medium.com/debian-packaging-by-example-118c18f5dbfe
    - [conan install -c tools.graph:skip_binaries=False --deployer=mylicense_deployer](https://github.com/conan-io/conan/issues/18207)
    - https://docs.conan.io/1/reference/conanfile/tools/system/package_manager.html
    - https://github.com/conan-io/examples2/blob/main/examples/tools/system/package_manager/conanfile.py
    - https://docs.conan.io/2/reference/conanfile/methods/system_requirements.html
    - https://github.com/conan-io/conan/issues/5664
    - https://github.com/conan-io/conan/issues/14189
    - https://github.com/conan-io/conan/issues/3541
    - https://github.com/conan-io/conan-extensions/blob/main/extensions/deployers/
    - https://docs.conan.io/2/reference/extensions/deployers.html#reference-extensions-deployers
    - https://docs.conan.io/2/examples/extensions/deployers/dev/development_deploy.html#examples-extensions-builtin-deployers-development
    - https://github.com/bkircher/python-rpm-spec

!!! question "Questions and Ideas"

    - Installing toolchain RPM dependencies in advance of build
      - https://docs.conan.io/2/reference/tools/system/package_manager.html

!!! note annotate "Reference"

    - https://docs.conan.io/2/reference/conanfile/methods/deploy.html
    - https://github.com/conan-io/conan-center-index/blob/master/recipes/gcc/all/conanfile.py


## Other

!!! question "ToDo"

    - allow package to provide custom RPM spec template
      - special dependencies
      - custom file permissions?  setuid/setgid, etc.  lsof/top?

!!! note annotate "Reference"

    - https://backreference.org/2011/09/17/some-tips-on-rpm-conditional-macros/index.html
    - https://rpm-software-management.github.io/rpm/manual/macros
    - https://rpm-packaging-guide.github.io/#packaging-software
    - https://rpm-packaging-guide.github.io/
    - https://docs.redhat.com/fr/documentation/red_hat_enterprise_linux/9/html/packaging_and_distributing_software/assembly_what-a-spec-file-is_packaging-software#ref_spec-file-preamble-items_assembly_what-a-spec-file-is
    - https://www.redhat.com/en/blog/create-rpm-package
    - https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/packaging_and_distributing_software/advanced-topics
