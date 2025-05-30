# Conan Setup and Recipe Pre-requisites

You will very likely need to maintain custom(ized) Conan recipes in order
to use this system.  If you are starting from scratch, you can find good
recipes to work from in the
[Conan Center Index](https://github.com/conan-io/conan-center-index/tree/master/recipes)

- Non-relocatable packages support `install_prefix` option
- Leverage `install_prefix` to configure compiler and toolchain PATH
- Install all dependencies in RPM form to `install_prefix`
- Disable Conan dependencies during `build`/`install`, replacing them with RPMs.

## `prefix` option in conanfile.py for each non-relocatable tool in the chain

- generate() for [`Autotools`](https://docs.conan.io/2/integrations/autotools.html)
  based tools needs to pass in this prefix when constructing `AutotoolsToolchain`

  ``` python
  if self.options.install_prefix:
      tc = AutotoolsToolchain(self, prefix=self.options.install_prefix)
  else:
      tc = AutotoolsToolchain(self)
  ```

!!! note annotate "Note"

    Derived from the [binutils conanfile.py](https://github.com/conan-io/conan-center-index/blob/master/recipes/binutils/all/conanfile.py#L36)
    but directly using the AutotoolsToolchain `prefix` attribute
    instead of `--program-prefix`.
    
    - https://github.com/conan-io/conan-center-index/blob/master/recipes/binutils/all/conanfile.py

## Local Recipe Index

Since we need to modify most recipes, you may wish to fork the public
ConanCenter recipe database.

- https://docs.conan.io/2/tutorial/conan_repositories/setup_local_recipes_index.html


## Custom profile for consistent prefix usage

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

## Local Conan recipe index

```bash
$ conan remote add conancenter-local ./conan-center-index
$ conan remote disable conancenter
```

## `toolchain` - Conan package

A special Conan package is created for your toolchain, and it will have
all of your desired tools listed as dependencies.

This special package provides the following:

- The complete list of all tool versions to be integrated.  Conan
  will validate and identify any version issues or cyclic dependencies.
- Dependency graph for our custom deployer script to process.
- Hook to trigger build/rebuild each package as appropriate.

We use this package as follows:
```bash
conan install --deployer-folder=<tmpdir> --deployer=rpm_deployer.py --profile toolchain --build=missing .
```

To deploy a single tool or subset of tools we can use `--deployer-package`:
```bash
conan install --deployer-folder=<tmpdir> --deployer-package="make/4.4.1" --deployer=rpm_deployer.py --profile toolchain --build=missing .
```

With a working `conanfile.py` for each tool in the toolchain, a single
`conan install` command can be used to build your entire toolchain.
