# Fresh Qwen3.8-27B download on the login node

Date: 2026-10-01 (America/New_York)

This continues the [compute-node download and network conversation](2026-10-01-qwen-download-and-network.md).

## User request

> I'm now on the login node instead of a compute node, please download the same model again, document the speed, compare against the prior speed on the compute node, and log the conversation to the  github repo

## Assistant actions and progress

Confirmed that the current host was `login1`. Its default internet route used `eth5`, which both sysfs and `ethtool` reported as a 10,000 Mb/s, full-duplex Ethernet link. The 1 Gb/s `eth2` interface and 200 Gb/s InfiniBand interface served separate internal subnets.

Selected the same Hugging Face repository and exact revision used on the compute node: `Qwen/Qwen3.8-27B`, revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`. Used a separate destination and a new Hugging Face/Xet cache to avoid reusing the existing downloaded model.

The first attempt used eight file workers, matching the earlier run. After approximately 20 seconds, progress showed about 16 GB allocated on disk. The process then exited with code 137. Memory diagnostics showed a 5 GiB user cgroup limit, a peak above that limit, and an out-of-memory kill count of one in both the user and session cgroups. These cumulative counters and the process exit indicate a memory-limit kill; no completed speed result was produced by this attempt.

The assistant reported the interruption and retried from scratch in another new destination with another new cache. The successful retry used two file workers and `HF_XET_NUM_CONCURRENT_RANGE_GETS=4` to lower concurrency. It did not resume the incomplete attempt.

Progress during the successful retry showed about 15.63 GB at 20 seconds, 33.50 GB at 40 seconds, and 48.94 GB at 60 seconds. These were allocated disk bytes, not isolated wire-byte measurements.

## Completed result and comparison

Downloaded all 32 files, totaling **55,586,114,863 bytes**, to:

`/lustre/nvwulf/scratch/decarlson/Qwen3.8-27B-login1-retry`

Every file size matched the repository metadata. This was size verification, not an independent checksum audit.

| Measurement | Compute node `b40x4-07` | Login node `login1` |
|---|---:|---:|
| Internet link | 1 Gb/s | 10 Gb/s |
| Model file bytes | 55,586,114,863 | 55,586,114,863 |
| Successful download time | 408.66 seconds | 67.14 seconds |
| Average effective file throughput | 136.02 MB/s | 827.95 MB/s |
| Binary-unit throughput | 129.72 MiB/s | 789.60 MiB/s |
| File workers | 8 | 2 |
| Xet range requests per file | Unset; documented default 16 | Explicitly 4 |
| Hugging Face Hub version | 1.31.0 | 1.31.0 |
| hf-xet version | 1.6.0 | 1.6.0 |

The login-node download was **6.0871 times as fast** and took **83.57% less time**, saving about **341.53 seconds** (5 minutes 42 seconds).

The successful retry started at `2026-10-01T10:39:49.513683+00:00` and finished at `2026-10-01T10:40:56.650386+00:00`. Speed is total completed file bytes divided by the wall-clock duration of `snapshot_download`. The initial interrupted attempt, metadata preflight, and subsequent verification are outside this successful-run timer.

## Interpretation and limitations

The login node's 10 Gb/s link has a theoretical raw ceiling of 1,250 MB/s before protocol overhead. Its effective download rate of about 828 MB/s is consistent with that link and substantially faster than the earlier compute-node result.

Host-wide receive counters increased by 50,997,171,360 bytes on `eth5`, equivalent to about 6.08 Gb/s over the timed interval. InfiniBand receive counters did not increase. The Ethernet counters support use of the internet interface, but include unrelated host activity and may lag; they are not exact per-process wire accounting.

As in the earlier run, Xet can transfer compressed chunks, so completed file bytes and network bytes need not match. The original compute-node effective rate of 136 MB/s exceeded its 1 Gb/s raw ceiling; the earlier conversation explains why that cannot be interpreted as raw wire speed.

The node, network path, available resources, and concurrency settings differ between the completed runs. This is a comparison of measured end-to-end downloads, not a controlled experiment attributing the entire speedup to link capacity. The login-node result excludes the interrupted attempt and uses a fresh cache and destination.

The original compute-node copy remains in `Qwen3.8-27B`. The interrupted login-node attempt remains in `Qwen3.8-27B-login1`; it is incomplete and should not be used as a complete model. The verified complete login-node copy is `Qwen3.8-27B-login1-retry`.

## Saved evidence

- [Login-node download metrics, network counters, comparison, and interruption diagnostics](../results/2026-10-01/login1-download-metrics.json)
- [Original compute-node download metrics](../results/2026-10-01/download-metrics.json)
- [Download script with the successful retry's concurrency settings](../scripts/download_qwen38_login.py)

The reproduction script requires `login1`, an absent destination, and a fresh cache. Its default destination is the completed retry path, so a future fresh run needs a different destination. This script does not include credentials.

## Sources

- [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)
- [Hugging Face Xet chunk compression](https://huggingface.co/docs/xet/xorb)
- [Hugging Face environment variables and Xet range-request concurrency](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables)

The user's request is preserved verbatim; assistant progress messages and tool output are summarized. Model weights, caches, and SSH keys are excluded from the documentation repository.
