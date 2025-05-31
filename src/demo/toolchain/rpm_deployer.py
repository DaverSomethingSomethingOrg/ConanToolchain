######################################################################
# rpm_deployer.py
#
# Conan Custom Deployer script that copies each dependency's files
# into a directory tree like the example below. Transitive
# dependencies are included.
#
# Sample Usage:
#
#   $ conan install --deployer-folder=rpm_deploy \
#                   --deployer-package="gcc/15.1.0" \
#                   --deployer=rpm_deployer.py \
#                   --profile=optToolchain \
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

    # Set up RPM dev tree in a temporary HOME directory
    orig_HOME = os.environ['HOME']
    rpm_HOME = os.path.join(output_folder, 'RPM_HOME')
    os.environ['HOME'] = rpm_HOME

    # We'll share a single RPM dev tree for all toolchain packages
    mkdir(conanfile=conanfile,
          path=os.path.join(output_folder, 'RPM_HOME'),
         )

    subprocess.run(['rpmdev-setuptree'])

    for name, dependency_item in conanfile.dependencies.items():
        if dependency_item.package_folder is None:
            continue
        process_dependency(conanfile, output_folder, rpm_HOME, dependency_item)

    # restore original $HOME setting
    os.environ['HOME'] = orig_HOME


# Function to ensure we capture any transitive dependencies
def process_dependency(conanfile, output_folder, rpm_HOME, dependency_item):

    info_msg = 'Deployer Processing ' \
             + str(dependency_item) \
             + ': package_folder: ' \
             + str(dependency_item.package_folder)

    conanfile.output.info(info_msg)

    # If our dependency doesn't have a prefix option defined, we'll assume it's relocatable and use our toplevel install_prefix option
    toolchain_prefix = conanfile.options.install_prefix

    copy_pattern = None
    copy_dst = None

    dashed_rpm_toolnamever = f'toolchain-{ dependency_item.ref.name }-{ dependency_item.ref.version }'

    if 'install_prefix' in dependency_item.options:
        # Dependency has a install_prefix, we'll copy the files out of that area
        tool_prefix = dependency_item.options.install_prefix

        # strip leading '/' off install_prefix
        neutered_prefix = str(tool_prefix).lstrip("/")
        copy_pattern = f'{ neutered_prefix }/*'
        copy_dst = os.path.join(output_folder, dashed_rpm_toolnamever)
    else:
        # Dependency does NOT have a install_prefix, we'll use ours as an install subdirectory and copy to that

        # strip leading '/' off install_prefix
        neutered_prefix = str(toolchain_prefix).lstrip("/")
        copy_pattern = '*'
        copy_dst = os.path.join(output_folder, dashed_rpm_toolnamever, neutered_prefix)

    copy(conanfile=conanfile,
         src=dependency_item.package_folder,
         excludes=['conaninfo.txt', 'conanmanifest.txt'],
         dst=copy_dst,
         pattern=copy_pattern,
        )

    # We'll name each of our toolchain packages after ourselves.
    # We are "toolchain", "make" gets "toolchain-make" to avoid conflict with OS packages.
#        prefixed_name = f'{ conanfile.ref.name }-{ dependency_item.ref.name }'
    prefixed_name = f'{ "toolchain" }-{ dependency_item.ref.name }'

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
    tool_dependencies = []
    for dep_name, dep_dep in dependency_item.dependencies.items():

        # Check if Conan thinks it's really a runtime dependency we need
        if dep_dep.package_folder is None:
            continue

        prefixed_dep_name = f'{ "toolchain" }-{ dep_dep.ref.name }'
        tool_dependencies.append(f'Requires: { prefixed_dep_name } = { dep_dep.ref.version }')

    if tool_dependencies:
        conanfile.output.info('Detected RPM dependencies:')
        for require_line in tool_dependencies:
            conanfile.output.info(f'\t{ require_line }')

    ######################################################################
    # Call `rpmbuild` against our parameterized/generic RPM spec file,
    # passing any of the metadata from `conanfile.py` as necesary.
    #
    # - set QA_RPATHS - Turn off any failing RPATH checks 
    # - disable __brp_mangle_shebangs, it doesn't work for packages like
    #   cmake and causes more harm than good.
    #
    os.environ['QA_RPATHS'] = "0x0020"
    rpmbuild_cmd = [
        'rpmbuild',
        '-bb',
        '--define', f"__brp_mangle_shebangs /bin/true",
        '--define', f"tool_name { prefixed_name }",
        '--define', f"tool_version { dependency_item.ref.version }",
        '--define', f"tool_description { dependency_item.description }",
        '--define', f"tool_license { dependency_item.license }",
        '--define', f"toolchain_prefix { toolchain_prefix }",
        '--define', f"build_num 1",
    ]

    if tool_dependencies:
        rpm_tool_dependencies_arg = 'tool_dependencies '

        for require_line in tool_dependencies:
            rpm_tool_dependencies_arg += f'{ require_line }\n'

        rpmbuild_cmd.extend(['--define', rpm_tool_dependencies_arg])

    rpmbuild_cmd.append(
        os.path.join('/workspaces/ConanToolchain/src/demo/toolchain', 'generic-v1.0.0.spec'),
    )

    conanfile.output.info('Executing rpmbuild: ' + str(rpmbuild_cmd))
    subprocess.run(rpmbuild_cmd)

#TODO throw exception on rpmbuild failure
