# Demo - Conan and ZFS and Kubernetes oh my!

<!-- markdownlint-disable MD046 -->
<!-- markdownlint-disable MD034 -->

## Introduction

Continuing our work with [Conan and ZFS](ConanZFSDemo.md), we'll explore
implementing this same solution in a Kubernetes environment.

Specifically we'll look at two topics

- GitHub Actions Runner Controller (ARC) for CI use
- OpenEBS with Local PV ZFS plugin

We'll skip over most of the boilerplate and default setup and focus on
just the special configurations required for leveraging our ZFS Conan
Cache in Kubernetes effectively.

## Environment

### Hardware

We'll be using the same hardware as our last demo.  We've added a few
new services onto our server, but at idle we're still using only 10GB
of RAM and just a fraction of a single CPU core.

- Server - 8945HS/64GB/SSD
- Workstation - 9900X/32GB/SSD
- Notebook - Macbook Pro M4 Pro
- Network - Ubiquiti UniFi 2.5Gb/s Switch

![server load screencap](img/server_idle_load.png)

### Software

- [GitHub Actions Runner Controller (ARC)](https://github.com/actions/actions-runner-controller/blob/master/README.md)
- [Sonatype Nexus Community Edition](https://www.sonatype.com/products/nexus-community-edition-download)
- [OpenZFS](https://openzfs.org/) filesystem and storage platform
- [OpenEBS](https://openebs.io/) with [Local PV ZFS plugin](https://github.com/openebs/zfs-localpv/blob/develop/README.md)
- [Conan C/C++ Package Manager](https://conan.io/)
- Docker - [ConanToolchain Docker Container Image](https://github.com/DaverSomethingSomethingOrg/conan-toolchain-demo/tree/main/demos/gcc-toolchain/conan-build-container/README.md)

## OpenEBS ZFS Setup

We'll reuse the ZFS installation from our previous demo, but we want to
create one toplevel dataset to clone from for our Runners and DevContainers.

#### ***TODO***

### Create snapshot and clone for our new build cache

#### ***TODO***

## GitHub Actions Runner Controller (ARC) for CI use

GitHub Actions Runner Controller is *complicated*, and not very well
documented.  See the References section for the most directly useful
documentation I found in setting this up.

To start with, we have a few different options we could implement to get
our desired functionality into GitHub Actions.

- Custom runner container image
- Runner Workflow hooks
- Runner Hook Extension

For this demo we'll take the simplest approach to implement, using a Runner
Hook Extension.  This is not necessarily the simplest option in terms of
technical implementation, but it gets us in business with the least amount
of customization and setup effort.

To accomplish this, we'll use GitHub ARC's `kubernetes` containerMode, and
leverage the Hook Extension template.  Using the Hook Extension template we
can attach our CONAN_HOME pvc to the job (workflow) container.

### Configure GitHub ARC RunnerScaleSet

First, we configure our RunnerScaleSet to run in `kubernetes` containerMode
and to look for our `github-arc-container-hooks` Hook Extension:

```yaml title="GitHub ARC kubernetes containerMode with Hook Extension Template"
containerMode:
  type: "kubernetes"

template:
  spec:
    containers:
    - name: runner
      image: ghcr.io/actions/actions-runner:latest
      command: ["/home/runner/run.sh"]
      env:
        - name: ACTIONS_RUNNER_CONTAINER_HOOKS
          value: /home/runner/k8s/index.js
        - name: ACTIONS_RUNNER_CONTAINER_HOOK_TEMPLATE
          value: /home/runner/pod-template/content
        - name: ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER
          value: "true"
      volumeMounts:
        - name: work
          mountPath: /home/runner/_work
        - name: container-hooks-volume
          mountPath: /home/runner/pod-template
    volumes:
    - name: work
      ephemeral:
        volumeClaimTemplate:
          spec:
            accessModes: [ "ReadWriteOnce" ]
            storageClassName: "local-path"
            resources:
              requests:
                storage: 1Gi
```

### Attach `$CONAN_HOME` PersistentVolumeClaim using Hook Extension

Next, we'll define our `$CONAN_HOME` PersistentVolumeClaim in a ConfigMap
within the same namespace as the RunnerScaleSet.

```yaml title="GitHub ARC Hook Extension ConfigMap"
apiVersion: v1
kind: ConfigMap
metadata:
  name: github-arc-container-hooks
data:
  content: |
    metadata:
      annotations:
        example: "extension"
        annotated-by: "extension"
      labels:
        labeled-by: "extension"
    spec:
      containers:
        - name: $job
          volumeMounts:
            - name: conan-home
              mountPath: /CONAN_HOME
          env:
            - name: CONAN_HOME
              value: /CONAN_HOME
      volumes:
        - name: conan-home
          ephemeral:
            volumeClaimTemplate:
              spec:
                accessModes: [ "ReadWriteOnce" ]
                storageClassName: "openebs-zfspv"
                dataSource:
                  name: gcc12-toolchain-main
                  kind: PersistentVolumeClaim
                resources:
                  requests:
                    storage: 200Gi
```

## GitHub Actions Workflow

For this demo I've implemented a simple GitHub Actions Workflow
[ConanZFSDemo-ARC.yml](https://github.com/DaverSomethingSomethingOrg/conan-toolchain-demo/blob/main/.github/workflows/ConanZFSDemo-ARC.yml).

Since all of the ZFS work is done by the Runner on job setup, we only need
to configure the `conan-toolchain.yml` workflow to locate our Conan Cache
PVC in `/CONAN_HOME`.

```yaml title="Configuring the conan-toolchain workflow to use our /CONAN_HOME PersistentVolumeClaim"
jobs:
  conan_toolchain:
    uses: DaverSomethingSomethingOrg/conan-github-workflows/.github/workflows/conan-toolchain.yml@main
    with:
      conan_home: "/CONAN_HOME"
      [...]
```

## Limitations and Open Issues

- The PVC and ZFS clone are removed at job completion (when the runner pod is destroyed).
    - https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.23/#ephemeralvolumesource-v1-core
    - Any builds/cache modifications that need to be kept will need to be saved outside of the runner prior to job completion.
        - Failed builds cannot be saved through the cache clone
- The PVC is provisioned against a fairly static clone defined in the Hook Extension ConfigMap
    - Organizational RunnerScaleSets will share the same cache
        - Multiple independent RunnerScaleSets will need to be set up to accommodate different parent clones.
    - good for efficiency and performance, but requires coordination to update the original volume

## Security

#### ***TODO***

Running as non-privileged user
- Runner container and job container need to have compatible securityContexts.
- Runner container runs actions (including containerized Actions), so Runner container generally needs to ensure that all actions containers and job containers run as the same UID.
It doesn't work when the actions/checkout container clones the repo as root but the workflow/build container runs non-privileged internally.

## Conclusions

#### ***TODO***

## What's Next

### Performance Optimization

While this solution demonstrates our ability to leverage ZFS for maximum
Conan build performance/avoidance, there are still a few steps we can take
to optimize GitHub ARC and Runner performance, especially in job startup
time.

### Cache Promotion

When we build updated components in our cloned cache, we're not able to
promote the updated clone to parent for future builds to leverage.

The ConfigMap we're using to identify the parent dataset to clone from can
certainly help us here, but we need to be careful to avoid race conditions
when doing so.  We don't want a clone being pulled from a cache that's in
the process of being updated!

### Saving Broken Builds for Troubleshooting

With this setup we have the advantage of having an entire Pod setup we
can use to reproduce issues.  Not only do we have the cache clone
available, we also have the container used for the build.

We'll want to work out a mechanism that allows our Runner Pods to persist
after job completion, but also be careful not to leave too many Runner Pods
laying around using up our cluster resources, even if they are idle.

## References

- https://docs.github.com/en/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets#using-kubernetes-mode
- https://docs.github.com/en/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets#configuring-hook-extensions
- https://upcloud.com/resources/tutorials/supercharge-your-ci-cd-deploy-lightning-fast-github-actions-runners-on-upclouds-managed-kubernetes-part-2/
- https://github.com/actions/actions-runner-controller/blob/master/charts/gha-runner-scale-set/values.yaml
