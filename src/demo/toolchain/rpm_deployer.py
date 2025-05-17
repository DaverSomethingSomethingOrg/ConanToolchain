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

        # tar up the deployment copy to use as rpmbuild sources
        subprocess.run(['tar',
                        '--create',
                        '--gzip',
                        '--file', os.path.join(rpm_HOME, 'rpmbuild', 'SOURCES', f'{ dashed_rpm_toolnamever }.tar.gz'),
                        '--directory', output_folder,
                        os.path.join(dashed_rpm_toolnamever, neutered_prefix)                        
                       ])

        # rpm spec template populated with information from conanfile
        # - build # or bootstrap versioning needs to be provided or detected somehow
        # - Source0, Summary, Description, arch, name, version, prefix
        # - %changelog ???
        # - author, source, license, name, version, prefix, dependencies

#TODO  rpmbuild -bb /workspaces/3ptyBuild/components/RpmBuilder/make-v4.4.1/make-v4.4.1.spec

    # restore original $HOME setting
    os.environ['HOME'] = orig_HOME

