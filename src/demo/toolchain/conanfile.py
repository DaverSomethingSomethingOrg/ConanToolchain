from conan import ConanFile
from conan.tools.cmake import cmake_layout
#from conan.tools.system import package_manager

class Toolchain(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    options = {
        "prefix": [None, "ANY"],
    }
    default_options = {
        "prefix": None,
    }
	
    def requirements(self):
        self.requires("make/4.4.1")
        self.requires("gcc/15.1.0")

    # https://docs.conan.io/1/reference/conanfile/tools/system/package_manager.html
    #def system_requirements(self):

#        dnf = package_manager.Dnf(self)
#        dnf.install(["ncurses-devel"], update=True, check=True)

#        yum = package_manager.Yum(self)
#        yum.install(["ncurses-devel"], update=True, check=True)

#        apt = package_manager.Apt(self)
#        apt.install(["libncurses-dev"], update=True, check=True)

#        pacman = package_manager.PacMan(self)
#        pacman.install(["ncurses"], update=True, check=True)

#        zypper = package_manager.Zypper(self)
#        zypper.install(["ncurses"], update=True, check=True)

#        brew = package_manager.Brew(self)
#        brew.install(["ncurses"], update=True, check=True)

#        pkg = package_manager.Pkg(self)
#        pkg.install(["ncurses"], update=True, check=True)

    def layout(self):
        cmake_layout(self)
