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
