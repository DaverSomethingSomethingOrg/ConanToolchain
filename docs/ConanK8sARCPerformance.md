# Demo - Securing and Performing with our GitHub ARC deployment

<!-- markdownlint-disable MD046 -->
<!-- markdownlint-disable MD034 -->

## Introduction

Continuing our work with [GitHub ARC with ZFS and Conan](ConanK8sARCDemo.md).

This time we'll explore optimizing the Performance and Security of our GitHub
ARC deployment, now that our product build is optimized.

!!! quote annotate ""

    ![Conan and ZFS in GitHub ARC box diagram](img/GitHubARCRunnerK8sContainerized.png)

    *Check out [Excalidraw](https://excalidraw.com/) and their nifty diagramming tool!*

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

## Enabling Debugging

### GitHub ARC built-in debugging

We'll start by enabling the maximum logging GitHub Actions can provide.
We'll add two new variable definitions to the repo for GitHub Actions to use.

- https://docs.github.com/en/actions/how-tos/monitor-workflows/enable-debug-logging

| Variable | Value |
| -------- | ----- |
| `ACTIONS_RUNNER_DEBUG` | "true" (string) |
| `ACTIONS_STEP_DEBUG` | "true" (string) |

![GitHub Repo Actions Variables](img/github_repo_variables.png)

## Performance

### Areas to look at

  - time to start new Runner
  - time for job to arrive at Runner
  - time to initialize workflow/$job container
    - caching Actions themselves
    - caching Actions externals/dependencies
  - time to start running job
  - time to cleanup after job

### Breaking it down

While GitHub doesn't provide granular timing data in its logs, we can see
precise timestamps for each log entry by pressing `Shift + T` while on the
job log screen.

![alt text](img/github_initialize_containers.png)

Breaking this down, we can see where the majority of the time is going:

```text
Tue, 23 Dec 2025 17:13:51 GMT ##[debug]Job pod created, waiting for it to come online linux-x86-64-dmdc5-runner-zdjp2-workflow
Tue, 23 Dec 2025 17:14:06 GMT ##[debug]Job pod is ready for traffic
```

For this particular job, 15s of the total 17s of the "Initialize
containers" step is spent waiting for the created Pod to start running.

### Instrumenting GitHub ARC kubernetes hook

- custom Runner container image

### Profiling End-to-End workflow/job runtime

containerd logs
kubectl pod logs/events
observability setup

### Runner caching for startup

- container image caching
- seeding GitHub Runner externals
  - cp -R /home/runner/externals /home/runner/_work/externals
  - claims that copying externals can be slow, that's not the case here...virtually instantaneous
    - probably related to using "local" storage for everything on a fast NVMe SSD

- waiting time seems to be entirely getting the pod from created/pending to running
- seeding GitHub Runner actions downloading

- backoff timing means we're sleeping longer than necessary
  - start with a more reasonable default wait time to avoid wasting the first backoff rounds

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

## Conclusions

## References

- Somersall, Natalie; [Securing Self-Hosted GitHub Actions with Kubernetes and Actions-Runner-Controller](https://some-natalie.dev/blog/securing-ghactions-with-arc/)

- Harsh, Kumar; [Supercharge Your CI/CD: Deploy Lightning-Fast GitHub Actions Runners on UpCloud’s Managed Kubernetes: Part 2](https://upcloud.com/resources/tutorials/supercharge-your-ci-cd-deploy-lightning-fast-github-actions-runners-on-upclouds-managed-kubernetes-part-2/)