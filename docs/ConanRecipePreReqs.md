# Conan Setup and Recipe Pre-requisites

You will very likely need to maintain custom(ized) Conan recipes in order
to use this system.  If you are starting from scratch, you can find good
recipes to work from in the
[Conan Center Index](https://github.com/conan-io/conan-center-index/tree/master/recipes)

## `install_prefix` option in conanfile.py for each non-relocatable tool in the chain

Non-relocatable packages require support for our `install_prefix` option.

For GNU tools, the Conan [`Autotools`](https://docs.conan.io/2/integrations/autotools.html)
integration already supports the autoconf `--prefix` option, so it's a
simple recipe modification.  Again, while it's ideal to use across all
tools, most GNU tools are relocatable and do not require this modification.

- generate() needs to pass in this prefix when constructing `AutotoolsToolchain`

  ``` python
  if self.options.install_prefix:
      tc = AutotoolsToolchain(self, prefix=self.options.install_prefix)
  else:
      tc = AutotoolsToolchain(self)
  ```

!!! warning annotate "Non-standard Conan Usage"

    Conan specifically tries to avoid hardcoding installation prefix into
    its builds.  For the standard Conan use-case supporting product
    development and release, hardcoded paths work against portability.

    When adding support for our `install_prefix` option, make sure to do
    so in a way that does not break the standard use case!

## Local Conan recipe index

Since we need to modify some recipes, you may wish to fork the public
ConanCenter recipe database if you're not writing your own recipes from
scratch.  You will need custom recipes for any special build configurations
not already supported by package options,

- https://docs.conan.io/2/tutorial/conan_repositories/setup_local_recipes_index.html

```bash
$ conan remote add conancenter-local ./conan-center-index
$ conan remote disable conancenter
conancenter: https://center2.conan.io [Verify SSL: True, Enabled: False]
$ conan remote list
conancenter: https://center2.conan.io [Verify SSL: True, Enabled: False]
conancenter-local: /workspaces/ConanToolchain/src/demo/toolchain/conan-center-index [local-recipes-index, Enabled: True]
$ 
```

### Maintaining the Conan Package Index

```none title="Sample Conan Package Index Directory Tree"
recipes
├── gcc
│   └── all
│       ├── conandata.yml
│       ├── conanfile.py
│       └── test_package
└── binutils
    └── all
        ├── conandata.yml
        ├── conanfile.py
        └── test_package
```

## Common Issues with conan-center-index packages for System Package deployment

### license File Conflicts

It looks like conan-center-index packages like to store a copy of their license
files into a common path /opt/toolchain/licenses/.  So we need to make sure our
ownership of such files is minimized to avoid conflicts.

```bash hl_lines="7 10"

root@927e783639d8:/workspaces/conan-system-packaging/demo# dpkg --install deb_deploy/*.deb
(Reading database ... 29691 files and directories currently installed.)
[...]
Preparing to unpack .../opt+toolchain-mpfr_4.2.0-1_arm64.deb ...
Unpacking opt+toolchain-mpfr (4.2.0-1) ...
dpkg: error processing archive deb_deploy/opt+toolchain-mpfr_4.2.0-1_arm64.deb (--install):
 trying to overwrite '/opt/toolchain/licenses/COPYING.LESSER', which is also in package opt+toolchain-mpc 1.2.0-1
[...]
dpkg: error processing archive deb_deploy/opt+toolchain-zlib_1.3.1-1_arm64.deb (--install):
 trying to overwrite '/opt/toolchain/licenses/LICENSE', which is also in package opt+toolchain-isl 0.26-1
[...]
root@927e783639d8:/workspaces/conan-system-packaging/demo# 

```

#### Fixing it in conanfile.py

This is the ideal option, but implies you are now forked from
`conan-center-index` and off to the races keeping your fork up-to-date.
Take heart, brave solider!

In the case of zlib, the simplest path is to just behave differently if
our `install_prefix` option is specified.  This is not a very self-defending
approach though.  Package maintainers not needing `install_prefix` might
not pay attention to `install_prefix`-related regressions.
 
```diff title="Sample Conan Package Index Directory Tree"

root@927e783639d8:/workspaces/conan-system-packaging/demo/conan-center-index# git diff recipes/zlib/all/conanfile.py
diff --git a/recipes/zlib/all/conanfile.py b/recipes/zlib/all/conanfile.py
index 717b2e9d8..c67082c9a 100644
--- a/recipes/zlib/all/conanfile.py
+++ b/recipes/zlib/all/conanfile.py
@@ -21,10 +21,12 @@ class ZlibConan(ConanFile):
     options = {
         "shared": [True, False],
         "fPIC": [True, False],
+        "install_prefix": [None, "ANY"],
     }
     default_options = {
         "shared": False,
         "fPIC": True,
+        "install_prefix": None,
     }
 
     def export_sources(self):
@@ -87,7 +89,11 @@ class ZlibConan(ConanFile):
         return license_contents
 
     def package(self):
-        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
+        if self.options.install_prefix:
+            save(self, os.path.join(self.package_folder, "licenses", self.name, "LICENSE"), self._extract_license())
+        else:
+            save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
+
         cmake = CMake(self)
         cmake.install()
 
root@927e783639d8:/workspaces/conan-system-packaging/demo/conan-center-index#

```

#### Overriding it in deployer

This is our fail-safest option, where we hardcode specific paths to ignore
or modify as appropriate.  We'll have to figure out a better solution
eventually.

```diff
     # Copy the package content out of the Conan cache
     copy(conanfile=conanfile,
          src=dependency_item.package_folder,
          excludes=['conaninfo.txt',
                    'conanmanifest.txt',
                    'conan*.sh',
                    'deactivate_conan*.sh',
                   ],
          dst=pkg_dst,
          pattern=copy_pattern,
         )
 
+    # CONFLICT Avoid - Move typically reused license file paths to package-specific paths
+    for license_file in ['COPYING', 'LICENSE', 'LICENSES', 'COPYING.LESSER', 'COPYING.LESSERv3', 'COPYINGv2',]:
+        if os.path.exists(os.path.join(pkg_dst, 'licenses', license_file)):
+            mkdir(conanfile=conanfile,
+                  path=os.path.join(pkg_dst, 'licenses', dependency_item.ref.name),
+            )
+            rm(conanfile=conanfile,
+               folder=os.path.join(pkg_dst, 'licenses', dependency_item.ref.name),
+               pattern=os.path.join(license_file),
+            )
+            rename(conanfile=conanfile,
+                   src=os.path.join(pkg_dst, 'licenses', license_file),
+                   dst=os.path.join(pkg_dst, 'licenses', dependency_item.ref.name, license_file),
+            )
+            rm(conanfile=conanfile,
+               folder=os.path.join(pkg_dst, 'licenses'),
+               pattern=os.path.join(license_file),
+            )
+
     # Copy the template content from the deployer installation
     copy(conanfile=conanfile,
          src=deb_template_path,
root@927e783639d8:/workspaces/conan-system-packaging# 
```

### Other Conflicts

```bash

[root@26c288a0b66e demo]# rpm --install --package rpm_deploy/RPM_HOME/rpmbuild/RPMS/aarch64/opt-toolchain-*rpm
        file /opt/toolchain/share/info/dir conflicts between attempted installs of opt-toolchain-binutils-2.42-1.el9.aarch64 and opt-toolchain-make-4.4.1-1.el9.aarch64
[root@26c288a0b66e demo]# 

```
