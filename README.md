# Toolchain Build System using Conan

The goal is to ensure that the tools the developers use are built using
the same configurations as the 3rdParty software being integrated into
the products.  With AI/ML workloads integrating Python in many areas,
it becomes important for the Python build to be ABI / link-compatible
with the product for instance.

## Why Prefix?

While a great deal of software is written in relocatable form these days,
there is still a long way to go.  Tools such as GCC need to be able to
locate it's libraries, as well as tools like `as` and `ld` from a different
package (binutils).  Relying on `$PATH` or `$ORIGIN` may not be sufficient
to locate the right ones.

For more in-depth discussion of the issues in maintaining an Enterprise
Engineering Development toolchain, and the benefits of this solution,
I've tried to cover it here:

- [But Why?](docs/ButWhy.md)
- [Sample Usage](docs/SampleUsage.md)
- [Conan Setup and Recipe Pre-requisites](docs/ConanRecipePreReqs.md)
