######################################################################
# nfs_deployer.py
#
# This deployer just drops all files into the given prefix, there
# is no package management available with this deployer.
#
# If you're developing in a container, the OS package-managed deployers
# are probably a better option for Software Composition Analysis to
# be able to track.
#

from conan.tools.files import copy
import os

def deploy(graph, output_folder, **kwargs):

    conanfile = graph.root.conanfile
    
    # If our dependency doesn't have a prefix option defined, we'll assume it's relocatable and use ours
    my_prefix = conanfile.options.prefix

    # Note the kwargs argument is mandatory to be robust against future changes.
    for name, dep in conanfile.dependencies.items():

#TODO
#        if dep.folders is None or dep.folders.package_folder is None:
#            raise ConanException(f"Sources missing for {name} dependency.\n"
#                                  "This deployer needs the sources of every dependency present to work, either building from source, "
#                                  "or by using the 'tools.build:download_source' conf.")
        if dep.package_folder is None:
            continue

        if 'prefix' in dep.options:
            
            # Dependency has a prefix, we'll copy the files out of that area
            my_prefix = dep.options.prefix

            # strip leading '/' off prefix
            neutered_prefix = str(my_prefix)[1:None]
            copy(conanfile=graph.root.conanfile,
                 pattern=f'{ neutered_prefix }/*',
                 src=dep.package_folder,
                 dst=os.path.join(output_folder),
                )
        else:
            # Dependency doesn't have a prefix, we'll use ours as an install subdirectory and copy to that

            # strip leading '/' off prefix
            neutered_prefix = str(my_prefix)[1:None]
            copy(conanfile=graph.root.conanfile,
                 pattern=f'*',
                 src=dep.package_folder,
                 dst=os.path.join(output_folder, neutered_prefix),
                 excludes=['conan*.txt'],
                )
