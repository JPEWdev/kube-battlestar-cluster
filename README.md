Battlestar Kubernetes Cluster
=============================
The configuration of my home bare metal kubernetes cluster

**NOTE** There are some security implications to be aware of if you are copying
this configuration! See below.

A possibly out of date description of the Cluster hardware
----------------------------------------------------------
**Master Node (galactica):** Dell R610, Dual Xeon X5670 @ 2.93 GHz, 120 GB RAM

**Worker Nodes (starbuck, viper):** Dell R610, Dual Xeon X5670 @ 2.93 GHz, 72 GB RAM

**Labgrid Coordinator Edge Node (coordinator-labgrid):** Dell Optiplex 7040, i7-6700 @ 3.7 GHz, 16 GB RAM

**Labgrid Exporter Edge Node (pirate-exporter-labgrid):** Rapsberry Pi 4, 4 GB RAM (currently unused)

The labgrid nodes are attached to my [PiRATE test boards](https://wattissoftware.blogspot.com/search/label/PiRATE)

What does this do?
------------------
The primary purpose of this cluster is to demonstrate a Kubernetes based CI
setup for building and testing embedded products with [the Yocto Project](https://www.yoctoproject.org/)

The idea is that you can describe and entire CI pipeline that will run anywhere
(Cloud Provider, Bare Metal, etc.) with minimal changes. The CI pipeline should
be able to build everything required, and also run CI tests on remote devices
that do not need to be co-located with the cluster (e.g. imagine you wanted to
do your builds in the cloud, but have it test on hardware located next to your
desk)

To test out these concepts, this cluster is setup to build [a Yocto DOOM Demo](https://github.com/JPEWdev/yocto-doom-demo),
but could be configured to build other projects

How does it work?
-----------------
The CI pipeline is setup using [Tekton](https://tekton.dev/). Builds are fairly
straight forward, with typical clone/build tasks. Testing of remote devices is
using [Labgrid](https://labgrid.readthedocs.io/en/latest/). The Tekton pipeline
runs [tests](https://github.com/JPEWdev/yocto-doom-demo/tree/main/ci) using
pytest with the Labgrid plugin, and it connects to a remote Labgrid coordinator
over ssh. The coordinator is also the SSH proxy for the labgrid exporter(s)
(although, currently the exporter and the coordinator are the same device). The
Labgrid nodes are attached to the cluster as edge nodes using
[KubeEdge](https://kubeedge.io/), which allows orchestrating them using
Kubernetes. Finally, testing of x86 emulated devices is done using
[KubeVirt](https://kubevirt.io/) to allow the testing image to run QEMU using
KVM acceleration.

Whats left to do?
-----------------
Mostly everything works now, but I have a few things I'd like to do yet:
 * Get webhooks working with GitHub/Tekton so it will build from GitHub events
   (see the security implications)
 * Figure out a way to automatically cleanup old builds. My cluster has pretty
   limited disk space. Right now, I have to manually delete all the
   PipelineRuns before I trigger more or I run our of PersistantVolumeClaims.
   Ideally, it would only keep around one of each build type and delete them
   when a new on appears
 * Try building on CEPH volumes using [ROOK](https://rook.io/). This would give
   a more "cloud" like expirence, since it would allow a pipeline's tasks to be
   run on different nodes (currently, a pipeline is locked to a specific node
   because it's using a local volume). This would optimize build scheduling,
   but I'm curious how the I/O will affect build times. I'm waiting on this
   until I get a LCAP-enabled switch so I can gang 4x1GbE links between build
   nodes
 * Figure out a better way of managing the Kubernetes deployment. I'm a
   complete K8s noob, but I couldn't find anything that easily let me describe
   my *entire* clusters configuration and manage it (I've already rebuilt the
   entire thing 2 or 3 times) sanely, so I wrote the deploy script. I don't
   like it... someone please point me to something better.

Security Implications
---------------------
 * The build pipeline is setup to use Tekton secrets for the labgrid SSH
   private key. However, since it is executing code from a GitHub repo, **it is
   trivial to exfiltrate those keys outside of the cluster** which would give
   anyone access to your Labgrid cluster. I would **not** recommend running
   these pipelines on **any** untrusted repos (e.g. pull requests). It's on my
   TODO list to resolve this, probably by moving the keys to a sidecar running
   SSH agent


Why is it named this?
---------------------
I needed a naming scheme, so I named my cluster nodes after Battlestar
Galactica characters/ships
