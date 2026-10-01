# Network layout explanation and download advice

Date: 2026-10-01 (America/New_York)

## User: speeding up compute-node downloads

> Is there anything I could do to speed up the download on the compute node?

## Assistant response, summarized

The most effective workflow is to download on the login node and use the completed copy from shared Lustre storage on the compute node. The observed login-node model download was 6.09 times faster. The compute node's 1 Gb/s internet link is the main constraint; the independent uncompressed test approached its usable capacity.

More workers or Xet's high-performance setting cannot bypass the Ethernet link limit. A faster compute-node internet path would require cluster infrastructure or routing support. InfiniBand serves an internal network and does not automatically provide faster internet access. Copying a model to local SSD can improve later loading, which is a separate operation from internet downloading.

## User: document the layout and push

> Please provide an explanation of the network layout, routes to the internet from different hosts (login and compute node) and a description of why the hosts differ in their network speeds.  Push this explanation to the repo

## Assistant actions and resulting explanation

Reviewed the earlier compute-node observations and saved download results. Rechecked the current login node's routes and Ethernet driver, link speeds, and addresses. Created [the network-layout explanation](../docs/network-layout.md), including a diagram, exact observed routes, hardware/link differences, measured download comparison, shared-storage workflow, and limitations.

The confirmed distinction is that `login1` sends internet traffic over 10 Gb/s `eth5` through gateway `130.245.181.1`, while `b40x4-07` uses 1 Gb/s `eth0` through gateway `10.10.0.211`. Both have an internal InfiniBand connection reporting 200 Gb/s. The gateway at `10.10.0.211` was not identified, and is not the login node's private address, `10.10.0.210`. Upstream routing and address translation were not inspected.

The explanation distinguishes measured host configuration from the inferred administrative rationale for giving different host roles different external connectivity. User requests are preserved verbatim; assistant actions and responses are summarized.
