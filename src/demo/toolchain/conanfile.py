from conan import ConanFile
#from conan.tools.cmake import cmake_layout
from conan.tools.layout import basic_layout
#from conan.tools.system import package_manager

class Toolchain(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
#    generators = "CMakeDeps", "CMakeToolchain"

    options = {
        "install_prefix": [None, "ANY"],
    }
    default_options = {
        "install_prefix": None,
    }

	
    def requirements(self):

        self.requires("make/4.4.1")
#        self.requires("zlib/1.3.1")
        self.requires("binutils/2.44")
        self.requires("gcc/15.1.0")

#        self.requires("autoconf/2.71")

#        self.requires("llvm-core/")
        self.requires("gtest/1.16.0")
#        self.requires("cppunit/1.15.1")
#        self.requires("valgrind/")

        self.requires("cmake/4.0.1")
#        self.requires("meson/1.7.2")
#        self.requires("ninja/1.12.1")
#        self.requires("bazel/7.2.1")
#        self.requires("flex/")
#        self.requires("bison/")

# conflict with cpython
#        self.requires("doxygen/1.14.0")

#        self.requires("patchelf/")
#        self.requires("openssl/")
#        self.requires("openjdk/21.0.2")

        self.requires("cpython/3.12.7")
        self.requires("nodejs/20.16.0")
#        self.requires("go/")
#        self.requires("rust/")

#        self.requires("curl/")
#        self.requires("wget/")
#        self.requires("git/")

#        self.requires("tar/")
#        self.requires("unzip/")
#        self.requires("7zip/")
#        self.requires("gzip-hpp/")
#        self.requires("xz/")

#        self.requires("gnupg/")
#        self.requires("coreutils/")
#        self.requires("diffutils/")
#        self.requires("gawk/")
#        self.requires("sed/")
#        self.requires("m4/")
#        self.requires("bzip2/")
#        self.requires("mingw-w64/")
#        self.requires("vim/")
#        self.requires("neovim/")
#        self.requires("openssh/")

    # https://docs.conan.io/2/reference/tools/system/package_manager.html

    def layout(self):
#        cmake_layout(self)
        basic_layout(self, src_folder="src")