# Demo - Conan and ZFS and Kubernetes CI (Oh my!)

<!-- markdownlint-disable MD046 -->
<!-- markdownlint-disable MD034 -->

## Introduction

Continuing our work with [Conan and ZFS](ConanZFSDemo.md) and
[OpenEBS and Kubernetes](ConanK8sDevContainerDemo.md), this time we'll
explore implementing a CI solution in our Kubernetes environment.

Specifically we'll leverage these two tools:

- GitHub Actions Runner Controller (ARC) for CI use
- OpenEBS with Local PV ZFS plugin

We'll skip over most of the boilerplate and default setup and focus on
just the special configurations required for leveraging our ZFS Conan
Cache in Kubernetes effectively.

!!! quote annotate ""

    ![Conan and ZFS in GitHub ARC box diagram](img/GitHubARCRunnerK8sContainerized.png)

    *Thanks to [Excalidraw](https://excalidraw.com/) for their nifty diagramming tool.*


## Environment

### Hardware

We'll be using the same hardware as our previous demos.

- Server - 8945HS/64GB/SSD
- Workstation - 9900X/32GB/SSD
- Notebook - Macbook Pro M4 Pro
- Network - Ubiquiti UniFi 2.5Gb/s Switch

We've added a few new services onto our server, but at idle we're still
using only 10GB of RAM and just a fraction of a single CPU core.

![server load screencap](img/server_idle_load.png)

Since we're making heavy use of build avoidance through caching, we're
able to use a power-efficient CPU and don't need a very elaborate storage
configuration.  We are running a significant number of processes however,
so we'll want to have a flexible number of CPU cores and a good amount
of memory.

### Software

- [GitHub Actions Runner Controller (ARC)](https://github.com/actions/actions-runner-controller/blob/master/README.md)
- [Sonatype Nexus Community Edition](https://www.sonatype.com/products/nexus-community-edition-download)
- [OpenZFS](https://openzfs.org/) filesystem and storage platform
- [OpenEBS](https://openebs.io/) with [Local PV ZFS plugin](https://github.com/openebs/zfs-localpv/blob/develop/README.md)
- [Conan C/C++ Package Manager](https://conan.io/)
- Docker - [ConanToolchain Docker Container Image](https://github.com/DaverSomethingSomethingOrg/conan-toolchain-demo/tree/main/demos/gcc-toolchain/conan-build-container/README.md)

## OpenEBS ZFS Setup

We'll reuse the ZFS installation from our previous demo, including the
toplevel dataset we created to clone our DevContainers from.

[Click here for more information](ConanK8sDevContainerDemo.md#openebs-zfs-setup)

!!! warning annotate

    OpenEBS does not support advanced ZFS operations such as `promote` or
    `rename`, so we'll need to look at a different approach to replace these
    parts of the workflow we used outside of Kubernetes.
    [Conan ZFS Demo Workflow](ConanZFSDemo.md#promote-the-successful-builds-clone)

## Comparing GitHub ARC Configurations

GitHub Actions Runner Controller is *complicated*, and not very
prolifically documented to be honest.  See the References section for the
most directly useful documentation I found in setting this up.

In order to work with our ZFS Conan cache using GitHub ARC Runners, we
first need to look at how the Runners behave.

There are a few fundamentally different ways to work with GitHub ARC
Runners, and we'll discuss a few of them here.

### `containerMode: kubernetes` with containerized workflows

First we'll look at `containerMode: kubernetes` with containerized workflows.
This mode has the distinct advantage over all other modes of waiting until
the workflow job starts in order to snapshot and clone the ZFS Conan cache.
This means the cache is the most up-to-date it can be, while keeping the
Runner processes warmed up and ready to go.

!!! note annotate "`containerMode: kubernetes` with containerized workflows"

    ![Conan and ZFS in GitHub ARC Containerized Workflow box diagram](img/GitHubARCRunnerK8sContainerized.png)

#### How it works

There's a lot going on here, but in a nutshell:

1. We set the `ACTIONS_RUNNER_CONTAINER_HOOKS` in the Runner container
   environment.  This will point to a wrapper script that the Runner will
   use to run our workflow actions and script steps rather than running
   then directly itself.  We'll use the hook included in the default
   Runner image
   [`/home/runner/k8s/index.js`](https://github.com/actions/runner-container-hooks/blob/main/packages/k8s/README.md)
1. `ACTIONS_RUNNER_CONTAINER_HOOK_TEMPLATE` points to our workflow pod spec
   "extension" to connect our ZFS cache PVC to the workflow `$job` container.
1. At job start time, our `k8s/index.js` wrapper creates the workflow pod
   and starts the `$job` container.
1. As the `$job` container is started, OpenEBS snapshots and clones our ZFS
   Conan cache DataSet as we specified in our hook extension.
1. `Runner.Worker` hands off the workflow job steps to the
   `k8s/index.js` wrapper for execution in the `$job` container.
1. Upon job completion, the ZFS cache PVC, `$job` container, and the
   runner and workflow jobs are all destroyed and resources freed up.

For all of this complex functionality, the configuration involved is
remarkably minimal.  Understanding how the Runner and hook operate is
critical to setting it up correctly, and troubleshooting any future
issues with your workflows.

### `containerMode: dind` with containerized workflows

!!! note annotate "`containerMode: dind`"

    ![Conan and ZFS in GitHub ARC box diagram](img/GitHubARCRunnerDinDContainerized.png)

#### ***TODO***

#### Issues

- Docker-in-Docker means no direct Kubernetes/OpenEBS integration
- Back to mounting local host paths into spawned container image

### Non-Containerized Workflows

Non-containerized workflows are very similar for both `containerMode: dind`
and `containerMode: kubernetes`.  The workflows run directly in the Runner
container.  In effect they are very similar to using the Runner container
as a dynamically scaled shell runner.

!!! note annotate "`Non-Containerized Workflows`"

    ![Conan and ZFS in GitHub ARC Non-Containerized Workflow box diagram](img/GitHubARCRunnerNonContainerized.png)

#### Issues with Non-containerized Workflows

Non-Containerized Workflows with GitHub ARC are sub-optimal for a variety
of reasons.

Customizing the Runner container capabilities requires providing a custom
Runner container image, or customizing it within the workflow.  Runner
containers need to be kept up-to-date with your installed GitHub version.
If you are maintaining your own hosted GitHub Enterprise Server (GHES)
instance, it's fairly straightforward to rebuild your runner container
images while upgrading GitHiub.  If you are using GitHub Enterprise Cloud,
you will need to ensure that your container images are updated on schedule
with GitHub's regular upgrades.
  
Second, similar to `containerMode: dind` we can mount our OpenEBS ZFS
Conan cache PVC to the Runner container, but this is done at Runner start
time, not job start time.  The snapshot will be as old as each Runner is
idle prior to recieving a job to run.

Third, security is minimal.  Your workflows are running with the same
privilege as your Runner processes.  While Kubernetes generally provides
a higher level of security in general to shell runners, this is still not
recommended.  We'll discuss GitHub ARC security in more detail in the
[Security](#security) section of this article.

For best results with our Conan cache it is recommended to fully disable
support for non-containerized workflows.

## Configuring GitHub ARC

For this demo we'll be using the `containerMode: kubernetes` with
containerized workflows configuration.  Having the Conan Cache snapshot
taken as late as possible (when the job starts) ensures that it is
current with the latest component builds available.

A second significant benefit to this approach is the ability to extend
the workflow pod configuration without having to redeploy or "upgrade"
our RunnerScaleSets, or even restart the runners.

### RunnerScaleSet Helm Chart values.yaml

First, we configure our RunnerScaleSet to run in `kubernetes` containerMode
and to look for our `github-arc-container-hooks` Hook Extension:

```yaml title="GitHub ARC kubernetes containerMode with Hook Extension Template" hl_lines="2 13-16 20-21 32-34"
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
    - name: container-hooks-volume
      configMap:
        name: github-arc-container-hooks
```

### Attach `$CONAN_HOME` PersistentVolumeClaim using Hook Extension

Next, we'll define our `$CONAN_HOME` PersistentVolumeClaim in a ConfigMap
within the same namespace as the RunnerScaleSet.

Modifying this ConfigMap is the mechanism we would use to replace the
`zfs promote` operation in our workflow.  We can simply swap out the PVC
parent clone `dataSource` the runner pod will snapshot from at job startup
time.  Managing the various OpenEBS ZFS datasets, snapshots, and clones
is beyond the scope of this demo however.  We'll stick to the mechanics
of leveraging an existing dataset.

Reference: [Mounted ConfigMaps are updated automatically](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#mounted-configmaps-are-updated-automatically)

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

Non-containerized workflows running with Runner privilege

Running as non-privileged user
- Runner container and job container need to have compatible securityContexts.
- Runner container runs actions (including containerized Actions), so Runner container generally needs to ensure that all actions containers and job containers run as the same UID.
It doesn't work when the actions/checkout container clones the repo as root but the workflow/build container runs non-privileged internally.

Links to GitHub ARC documentation on security best practices

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

By default these Runner and Workflow Pods are not persisted after job
completion.  We'll want to work out a mechanism that allows those Pods to
persist after job completion, but also be careful not to leave too many
Runner Pods laying around using up our cluster resources, even if they are
idle.

## References

- https://github.com/actions/actions-runner-controller/blob/master/docs/about-arc.md
- https://github.com/actions/actions-runner-controller/blob/master/docs/gha-runner-scale-set-controller/README.md
- https://github.com/actions/runner-container-hooks/blob/main/packages/k8s/README.md
- https://docs.github.com/en/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets#using-kubernetes-mode
- https://docs.github.com/en/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets#configuring-hook-extensions
- https://upcloud.com/resources/tutorials/supercharge-your-ci-cd-deploy-lightning-fast-github-actions-runners-on-upclouds-managed-kubernetes-part-2/
- https://github.com/actions/actions-runner-controller/blob/master/charts/gha-runner-scale-set/values.yaml