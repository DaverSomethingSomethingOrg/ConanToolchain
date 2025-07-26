# CI Workflows

!!! github-reference annotate "[conan-github-workflows](https://github.com/DaverSomethingSomethingOrg/conan-github-workflows)"

    Custom [GitHub Actions Reusable Workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows)
    to provide multi-platform build/test/release workflows for individual
    Conan builds, and for complete toolchain builds.

    - https://github.com/DaverSomethingSomethingOrg/conan-github-workflows

## Toolchain Workflow

[Link to `conan-toolchain.yml`](https://github.com/DaverSomethingSomethingOrg/conan-github-workflows/blob/main/.github/workflows/conan-toolchain.yml)

Our Conan Toolchain workflow is a simplified Conan CI workflow,
not intended to do any quality validation of the individual tools
in the toolchain.  If the tools are already available in the Conan
cache (this is adviseable for regular toolchain maintenance!),
this workflow will not even rebuild them.

For each tool in the toolchain, this workflow will run the specified RPM
or Debian package deployer and then cache the generated packages.


!!! note annotate "Basic Conan Toolchain Workflow"

    ![Conan Toolchain Workflow](img/conan_toolchain_workflow.png)

## Multi-Platform Toolchain Workflow

[Link to `conan-multiPlatformToolchain.yml`](https://github.com/DaverSomethingSomethingOrg/conan-github-workflows/blob/main/.github/workflows/conan-multiPlatformToolchain.yml)

Our Multi-Platform workflow allows us to selectively enable thre platforms
we would like to build on-demand.  We can also specify the toolchain
`install_prefix` to pass in to Conan.  From there it will simply run a
matrix of `conan-toolchain.yml` jobs, one for each platform in parallel.

!!! note annotate "Multi-Platform Conan Toolchain Workflow"

    ![Multi-Platform Conan Toolchain Workflow](img/conan_multiplatform_toolchain.png)

## Basic Operation

### Triggering a Toolchain Build (demo)

!!! github-reference annotate "Conan Toolchain Workflow Dispatch"

    ![GitHub Workflow Dispatch](img/github_workflow_dispatch.png)

!!! github-reference annotate "Conan Multi-Phase Multi-Platform Chart"

    ![Multi-Phase Multi-Platform Chart](img/github_workflow_chart.png)

!!! github-reference annotate "Conan Workflow Steps"

    ![Workflow Steps](img/github_workflow_steps.png)
