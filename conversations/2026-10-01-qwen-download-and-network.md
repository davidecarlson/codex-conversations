# Qwen3.8-27B download and network verification

Date: 2026-10-01 (America/New_York)

## Conversation

### User: download the model

> Use huggingface to download the Qwen/Qwen3.8-27B model in the current working directory and report the download speed once complete.

### Assistant: download results

Downloaded to `/lustre/nvwulf/scratch/decarlson/Qwen3.8-27B`.

- Size: **55.59 GB**, 32 files verified by size
- Time: **6 minutes 49 seconds**
- Average download speed: **136.0 MB/s** (129.7 MiB/s)

### User: verify network speed

> Try to check the available network speeds and confirm if the average 135.0 MB/s speed is consistent with the network.

### Assistant: network results

**The result is consistent as effective file throughput, but not as raw network speed.** The original measurement was **136.0 MB/s**.

| Check | Result |
|---|---|
| Internet interface (`eth0`) | **1 Gb/s**, full duplex |
| Ethernet theoretical maximum | **125 MB/s**, before overhead |
| InfiniBand (`ib0`) | **200 Gb/s**, internal network; unused by the transfer |
| Fresh 1 GiB Hugging Face test | **109.8 MB/s** overall; **115.7 MB/s** during streaming |

The fresh test fits the 1 Gb/s connection. The original download used Hugging Face's Xet client, which supports [compressed chunks](https://huggingface.co/docs/xet/xorb). Compression likely explains why reconstructed model bytes averaged 136 MB/s, above the raw link limit.

The original run didn't record network byte counters, so its exact wire speed cannot be confirmed retrospectively.

### User: preserve the conversation in GitHub

> Please create a github repo to document codex conversations, log the results of this conversation and push the results to the repo using davidecarlson username and my ssh key.

The requested repository is `davidecarlson/codex-conversations`. SSH authentication was verified: GitHub identified the existing SSH key as belonging to `davidecarlson`. Repository creation requires a separate GitHub API or browser session; SSH authenticates Git transport.

## Download method and evidence

Used `huggingface_hub.snapshot_download` with eight workers, pinned to revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`. The target directory initially contained no completed repository files. The client downloaded all 32 files, then checked each file's size against repository metadata. This was size verification, not an independent checksum audit.

| Measurement | Value |
|---|---|
| Repository | `Qwen/Qwen3.8-27B` |
| Total file bytes | 55,586,114,863 |
| Elapsed time | 408.664921182 seconds |
| Average effective file throughput | 136.018806562 MB/s |
| Binary-unit throughput | 129.717642367 MiB/s |
| Hugging Face Hub version | 1.31.0 |
| hf-xet version | 1.6.0 |

The average is total newly completed file bytes divided by the wall-clock duration of `snapshot_download`. It includes its metadata and transfer overhead; it does not measure compressed bytes on the network.

Evidence: [download metrics](../results/2026-10-01/download-metrics.json).

## Network verification method and evidence

The host was `b40x4-07`. Both sysfs and `ethtool eth0` reported 1000 Mb/s, full duplex. The Ethernet driver was `tg3`. Routing selected `eth0` for Hugging Face's public IP address. InfiniBand reported 200 Gb/s (2X NDR) and served a separate internal subnet.

A fresh HTTP range request fetched exactly 1 GiB from the first model shard through `us.aws.cdn.hf.co`. The server returned HTTP 206 with range `bytes 0-1073741823/3966730552`. The request used `Accept-Encoding: identity`, streamed the response, discarded its data, and left the downloaded model unchanged.

| Measurement | Value |
|---|---|
| Bytes read | 1,073,741,824 |
| Total elapsed time | 9.782584075 seconds |
| Overall throughput | 109.760551585 MB/s |
| Streaming elapsed time | 9.283919392 seconds |
| Streaming throughput | 115.656090780 MB/s |
| InfiniBand receive-counter delta | 0 bytes |

The JSON also contains interface counter samples. The sampled Ethernet delta is smaller than the application byte count, so those snapshots should not be treated as precise wire accounting for the test. The application byte count and elapsed time provide the reported transfer rate.

Evidence: [network test metrics](../results/2026-10-01/network-check.json).

## Interpretation and limitations

- A 1 Gb/s link has a theoretical ceiling of 125 MB/s before protocol overhead. Both 135 MB/s and the actual 136.0 MB/s exceed that raw ceiling.
- The fresh 109.8 MB/s overall and 115.7 MB/s streaming rates are consistent with the Ethernet link.
- Xet can transfer compressed chunks and reconstruct larger files locally. Compression is a plausible explanation for the original effective throughput; its exact contribution was not measured.
- The InfiniBand link's higher advertised speed does not establish higher internet bandwidth.
- No network byte counters were collected during the original model download, so its wire throughput cannot be reconstructed from the saved download metrics alone.

## Sources

- [Qwen/Qwen3.8-27B on Hugging Face](https://huggingface.co/Qwen/Qwen3.8-27B)
- [Hugging Face Xet chunk format and compression](https://huggingface.co/docs/xet/xorb)

Progress messages and tool tracebacks are summarized here; user requests and the completed result responses are preserved above. No credentials, private keys, or model weights are included.
