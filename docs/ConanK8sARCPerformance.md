# Demo - Securing and Performing with our GitHub ARC deployment

<!-- markdownlint-disable MD046 -->
<!-- markdownlint-disable MD034 -->

## Introduction

Continuing our work with [GitHub ARC with ZFS and Conan](ConanK8sARCDemo.md).

We've deployed GitHub Actions Runner Controller (ARC) along with OpenEBS and
OpenZFS in order to optimize our CI and Developer Sandbox build performance.

!!! note annotate "GitHub ARC with ZFS and Conan"

    ![Conan and ZFS in GitHub ARC box diagram](img/GitHubARCRunnerK8sContainerized.png)

    *Check out [Excalidraw](https://excalidraw.com/) and their nifty diagramming tool!*

This time we'll explore optimizing the Performance and Security of our GitHub
ARC deployment, now that our product build is optimized.

We'll also need to look at how it scales, and how it breaks.  How does cache
corruption spread though our clone structure?

## Environment

### Hardware

We'll be using the same hardware as our previous demos.  All performance
optimizations in this demo are done in the configuration, we're not doing
any hardware optimization.

- Server - AMD 8945HS/64GB/SSD
- Workstation - AMD 9900X/32GB/SSD
- Notebook - Macbook Pro M4 Pro
- Network - Ubiquiti UniFi 2.5Gb/s Switch

### Software

- [GitHub Actions Runner Controller (ARC)](https://github.com/actions/actions-runner-controller/blob/master/README.md)
- [OpenZFS](https://openzfs.org/) filesystem and storage platform
- [OpenEBS](https://openebs.io/) with [Local PV ZFS plugin](https://github.com/openebs/zfs-localpv/blob/develop/README.md)
- [Conan C/C++ Package Manager](https://conan.io/)
- Docker - [ConanToolchain Docker Container Image](https://github.com/DaverSomethingSomethingOrg/conan-toolchain-demo/tree/main/demos/gcc-toolchain/conan-build-container/README.md)
- [Sonatype Nexus Community Edition](https://www.sonatype.com/products/nexus-community-edition-download)

## General Performance

We want to look into other areas where we can improve performance of
our solution.  Performance is the primary goal of this project after all.

We'll look at the following areas for improvements:

  - time to start new Runner
  - time for job to arrive at Runner
  - time to initialize workflow/$job container
    - caching Actions themselves
    - caching Actions externals/dependencies
  - time to start running job
  - time to cleanup after job

### Profiling End-to-End workflow/job runtime

containerd logs
kubectl pod logs/events
observability setup

### Instrumenting the GitHub ARC kubernetes hook

- custom Runner container image for customized k8s hook
  - enhanced debugging
  - modified backoff schedule wastes less time sleeping
  - issues resolved

### Runner caching for startup

- container image caching
- seeding GitHub Runner externals
  - cp -R /home/runner/externals /home/runner/_work/externals
  - claims that copying externals can be slow, that's not the case here...virtually instantaneous
    - probably related to using "local" storage for everything on a fast NVMe SSD

- waiting time seems to be entirely getting the pod from created/pending to running
- seeding GitHub Runner actions downloading

- backoff aggressive timing means we're sleeping longer than necessary
  - start with a more reasonable default wait time to avoid wasting the first backoff rounds
  - reduce backoff wait ratio from 2x to 1.25x

- k8s-novolume?
  - is mounting the runner's work volume in the workflow container the problem?
  - k8s-novolume seems to have issues right now, not working.
    - faster in general tho...

### Workflow job container optimization

- actions caching
  - /__w/_actions/action/name/version ~ /__w/_actions/action/actions/checkout/v4
    - no .git subdir, just clean tag checkout

  - confirmed that actions/checkout@v4 works fine mounted from ZFS cache, BUT...

  - Runner downloads actions prior to running hook and creating workflow container?
    - if so we need to mount the actions cache to the runner as well as the workflow pod and make sure the actions are not downloaded anyway.
    - it can't slow down initializing the workflow container if the download is happening before the hook starts?
  - still good idea for reliability (reduce external dependency at job runtime), general job starting, and supply chain security

### kubectl in workflow pod initContainer?

### Specifying resource requests vs. limits

Does limiting resources start faster?

- Guaranteed Scheduling
- Custom scheduling?

## Security

Security is pretty well configured out of the box, but we'll review
common recommendations to make sure our solution still conforms, and
to take advantage of any features we've missed or mis0configured along
the way.

- Controller and RunnerScaleSet in different namespaces
- Running as non-privileged user
  - securityContext
- Runner container and job container need to have compatible securityContexts.
- Runner container runs actions (including containerized Actions), so
  Runner container generally needs to ensure that all actions containers
  and job containers run as the same UID.
- It doesn't work when the actions/checkout container clones the repo as
  root but the workflow/build container runs non-privileged internally.
- non-privileged workflow pods
- locking container versions away from latest
- minimal container images
    - minimal runner
    - minimal workflow
- no sudo in workflow
- custom crafted workflow containers not modifyable by workflow
- namespace vs. cluster isolation
- dind-rootless
- Links to GitHub ARC documentation on security best practices

## Performance and Security combined

- Container/Kubernetes means not needing to chown the cache files for developer end use.
- Importance of user-agnostic behavior
  - build is done "on behalf of" user, not executed directly by user account
  - generic, non-privileged userids own everything, run everything

## Troubleshooting Broken Builds

`ACTIONS_RUNNER_HOOK_JOB_COMPLETED` hook

To keep a container running indefinitely for debugging purposes, one common method involves overriding its entrypoint command to something like sleep infinity or tail -f /dev/null during setup, then using docker exec to interact with it. This is a manual debugging step, not an automated workflow configuration.

## Limitations and Open Issues

## What's Next

### Deploy solution for Bazel build cache

### Supply Chain - Dependency Track

### Switch to NetApp instead of OpenZFS and OpenEBS?

OpenZFS is great for prototyping and use on developer workstations, but
practically speaking it seems more likely that development environments
needing this level of build optimization probably have enterprise-grade
storage options available.

NetApp ONTAP with FlexClone is a more likely to be available in an
enterprise software development environment than OpenZFS.  It's also a
natural fit for this solution with it's patented snapshot and clone
technologies.

We should evaluate how well FlexClone fits into this solution.  Up until
this point we have been focusing on leveraging "free"/open technologies.


## Conclusions

## References

- Somersall, Natalie; [Securing Self-Hosted GitHub Actions with Kubernetes and Actions-Runner-Controller](https://some-natalie.dev/blog/securing-ghactions-with-arc/)

- Harsh, Kumar; [Supercharge Your CI/CD: Deploy Lightning-Fast GitHub Actions Runners on UpCloud’s Managed Kubernetes: Part 2](https://upcloud.com/resources/tutorials/supercharge-your-ci-cd-deploy-lightning-fast-github-actions-runners-on-upclouds-managed-kubernetes-part-2/)