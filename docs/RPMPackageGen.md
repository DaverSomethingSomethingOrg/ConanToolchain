# RPM / .deb Package Generation

## Confirmed

- `toolchain-` prefixed package name to avoid OS package conflicts
- Make sure to turn off AutoReqProv, we will specify dependencies by
  package name/version only.
- `%files` section merely specifies `prefix` (includes all contained
  subdirectories and files recorsively)

## Other

- translate conan runtime dependencies into RPM dependencies, assuming
  RPMs exist for each dependency.
  - Runtime dependencies should be installed in advance
  - Build dependencies should be installed, but not spec'd
    - Verify they exist/work in advance too!

- If Conan GCC depends on Conan binutils, first build binutils package
  and publish package.
- Pass Prefix into conan install/build, ensuring all toolchain tools
  have a consistent prefix.
  - Since we'll use non-default/standard prefix, we'll want to make sure
    we don't publish the Conan package beyond the cache.  It's only
    temporary to in order to deploy RPM packages from.
- Next yum install the binutils RPM into our prefix so it's available
  as a build dependency for GCC

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
