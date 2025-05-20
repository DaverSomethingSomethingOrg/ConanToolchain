######################################################################
# rpm_deployer.py
#
# Conan Custom Deployer script that copies each dependence's files
# into a directory tree like the example below. Transitive
# dependencies are included.
#
# Sample Usage:
# 
#   $ conan install --deployer-folder=rpm_deploy \
#                   --deployer-package="gcc/15.1.0" \
#                   --deployer=rpm_deployer.py \
#                   --profile=optPrefix \
#                   .
# 
# Sample Directory Tree Output:
# 
#   rpm_deploy
#   ├── toolchain-gcc-15.1.0
#   │   └── opt/toolchain
#   │       ├── bin
#   │       ├── include
#   │       ├── lib
#   │       ├── lib64
#   │       ├── libexec
#   │       └── share
#   └── toolchain-gmp-6.3.0
#       └── opt/toolchain
#           ├── include
#           ├── lib
#           └── licenses
#
#
#   rpm_deploy/RPM_HOME
#   └── rpmbuild
#       ├── RPMS
#       │   └── aarch64
#       │       ├── toolchain-gcc-15.1.0-1.el9.aarch64.rpm
#       │       ├── toolchain-gmp-6.3.0-1.el9.aarch64.rpm
#       │       ├── toolchain-isl-0.26-1.el9.aarch64.rpm
#       │       ├── toolchain-make-4.4.1-1.el9.aarch64.rpm
#       │       ├── toolchain-mpc-1.2.0-1.el9.aarch64.rpm
#       │       ├── toolchain-mpfr-4.2.0-1.el9.aarch64.rpm
#       │       └── toolchain-zlib-1.3.1-1.el9.aarch64.rpm
#       └── SOURCES
#           ├── toolchain-gcc-15.1.0.tar.gz
#           ├── toolchain-gmp-6.3.0.tar.gz
#           ├── toolchain-isl-0.26.tar.gz
#           ├── toolchain-make-4.4.1.tar.gz
#           ├── toolchain-mpc-1.2.0.tar.gz
#           ├── toolchain-mpfr-4.2.0.tar.gz
#           └── toolchain-zlib-1.3.1.tar.gz

from conan.tools.files import copy, mkdir
#from conan.errors import ConanException
import os
import subprocess

def deploy(graph, output_folder, **kwargs):

    conanfile = graph.root.conanfile
    
    # If our dependency doesn't have a prefix option defined, we'll assume it's relocatable and use ours
    toolchain_prefix = conanfile.options.prefix

    # Set up RPM dev tree in a temporary HOME directory
    orig_HOME = os.environ['HOME']
    rpm_HOME = os.path.join(output_folder, 'RPM_HOME')
    os.environ['HOME'] = rpm_HOME

    # We'll share a single RPM dev tree for all toolchain packages
    mkdir(conanfile=conanfile,
          path=os.path.join(output_folder, 'RPM_HOME'),
         )

    subprocess.run(['rpmdev-setuptree'])

    # Note the kwargs argument is mandatory to be robust against future changes.
    for name, dep in conanfile.dependencies.items():

#TODO
#        if dep.folders is None or dep.folders.package_folder is None:
#            raise ConanException(f"Sources missing for {name} dependency.\n"
#                                  "This deployer needs the sources of every dependency present to work, either building from source, "
#                                  "or by using the 'tools.build:download_source' conf.")
        if dep.package_folder is None:
            continue

        copy_pattern = None
        copy_dst = None
 
        dashed_rpm_toolnamever = f'toolchain-{ dep.ref.name }-{ dep.ref.version }'
 
        if 'prefix' in dep.options:
            # Dependency has a prefix, we'll copy the files out of that area
            tool_prefix = dep.options.prefix

            # strip leading '/' off prefix
            neutered_prefix = str(tool_prefix).lstrip("/")
            copy_pattern = f'{ neutered_prefix }/*'
            copy_dst = os.path.join(output_folder, dashed_rpm_toolnamever)
        else:
            # Dependency doesn't have a prefix, we'll use ours as an install subdirectory and copy to that

            # strip leading '/' off prefix
            neutered_prefix = str(toolchain_prefix).lstrip("/")
            copy_pattern = '*'
            copy_dst = os.path.join(output_folder, dashed_rpm_toolnamever, neutered_prefix)

        copy(conanfile=conanfile,
             src=dep.package_folder,
             excludes=['conaninfo.txt', 'conanmanifest.txt'],
             dst=copy_dst,
             pattern=copy_pattern,
            )

        # We'll name each of our toolchain packages after ourselves.
        # We are "toolchain", "make" gets "toolchain-make" to avoid conflict with OS packages.
#        prefixed_name = f'{ conanfile.ref.name }-{ dep.ref.name }'
        prefixed_name = f'{ "toolchain" }-{ dep.ref.name }'

        # tar up the deployment copy to use as rpmbuild sources
        subprocess.run(['tar',
                        '--create',
                        '--gzip',
                        '--file', os.path.join(rpm_HOME, 'rpmbuild', 'SOURCES', f'{ dashed_rpm_toolnamever }.tar.gz'),
                        '--directory', output_folder,
                        os.path.join(dashed_rpm_toolnamever, neutered_prefix)                        
                       ])

        # rpm spec template populated with information from conanfile
        #TODO
        # - build # or bootstrap versioning needs to be provided or detected somehow
        # - Summary, arch
        # - author, dependencies
        # - %changelog ???

        # Gather dependency list from conanfile.py for use in RPM spec `Requires:`
        # list with prefixed package names... 
        # 
        tool_dependencies = ""
        for dep_name, dep_dep in dep.dependencies.items():

            prefixed_dep_name = f'{ "toolchain" }-{ dep_dep.ref.name }'
            tool_dependencies += f'Requires: { prefixed_dep_name }-{ dep_dep.ref.version }\n'

        conanfile.output.debug(f'Detected dependencies: { tool_dependencies }')

        # Turn off any RPATH checks and so forth - GCC be breaking all the rulez
        os.environ['QA_RPATHS'] = "0x0020"

        # Call `rpmbuild` against our parameterized/generic RPM spec file,
        # passing any of the metadata from `conanfile.py` as necesary.
        subprocess.run(['rpmbuild',
                        '-bb',
                        '--define', f"tool_name { prefixed_name }",
                        '--define', f"tool_version { dep.ref.version }",
                        '--define', f"tool_description { dep.description }",
                        '--define', f"tool_license { dep.license }",
                        '--define', f"tool_dependencies { tool_dependencies }",
                        '--define', f"toolchain_prefix { toolchain_prefix }",
                        '--define', f"build_num 1",
                        os.path.join('/workspaces/ConanToolchain/src/demo/toolchain', 'generic-v1.0.0.spec'),
                       ])

    # restore original $HOME setting
    os.environ['HOME'] = orig_HOME

