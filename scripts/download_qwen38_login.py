import os
import socket
import json
import threading
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version

root = Path('/lustre/nvwulf/scratch/decarlson')
host = socket.gethostname()
if host.split('.')[0] != 'login1':
    raise RuntimeError(f'Expected login1, found {host}')
destination = root / 'Qwen3.8-27B-login1-retry'
if destination.exists():
    raise RuntimeError(f'Fresh download requires an absent destination: {destination}')
cache = root / '.cache' / ('huggingface-login1-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
if cache.exists():
    raise RuntimeError('Fresh download requires an absent cache')
os.environ['HF_HOME'] = str(cache)
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['HF_XET_NUM_CONCURRENT_RANGE_GETS'] = '4'
from huggingface_hub import HfApi, snapshot_download

repo = 'Qwen/Qwen3.8-27B'
revision = '1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0'
info = HfApi().model_info(repo, revision=revision, files_metadata=True)
expected = {f.rfilename: f.size for f in info.siblings if f.size is not None}
total = sum(expected.values())
def counters():
    result = {}
    for dev in Path('/sys/class/net').iterdir():
        try:
            result[dev.name] = {direction: int((dev / 'statistics' / f'{direction}_bytes').read_text()) for direction in ['rx', 'tx']}
        except OSError:
            pass
    return result

routes = subprocess.run(['ip', 'route'], capture_output=True, text=True).stdout
before = counters()
started_at = datetime.now(timezone.utc).isoformat()
start = time.perf_counter()
done = threading.Event()
def progress():
    while not done.wait(20):
        allocated = sum(p.stat().st_blocks * 512 for p in destination.rglob('*') if p.is_file()) if destination.exists() else 0
        print(f'PROGRESS elapsed={time.perf_counter()-start:.1f}s allocated={allocated/1e9:.2f}GB of {total/1e9:.2f}GB', flush=True)
thread = threading.Thread(target=progress, daemon=True)
thread.start()
print(f'Starting fresh download on {host}: {total:,} bytes; cache={cache}; destination={destination}', flush=True)
try:
    snapshot_download(repo_id=repo, revision=revision, local_dir=destination, max_workers=2)
finally:
    done.set()
    thread.join()
elapsed = time.perf_counter() - start
finished_at = datetime.now(timezone.utc).isoformat()
after = counters()
bad = [name for name, size in expected.items() if not (destination / name).is_file() or (destination / name).stat().st_size != size]
if bad:
    raise RuntimeError(f'File size verification failed: {bad}')
prior = json.loads((root / 'Qwen3.8-27B-download-metrics.json').read_text())
rate = total / elapsed / 1e6
metrics = dict(repo_id=repo, revision=revision, hostname=host, directory=str(destination), cache_directory=str(cache), fresh_destination=True, fresh_cache=True, files=len(expected), total_bytes=total, previously_complete_bytes=0, started_at_utc=started_at, finished_at_utc=finished_at, elapsed_seconds=elapsed, average_MB_per_second=rate, average_MiB_per_second=total/elapsed/2**20, max_workers=2, xet_concurrent_range_gets=4, speed_basis='new file bytes divided by snapshot_download wall-clock time', verified_file_sizes=True, huggingface_hub_version=version('huggingface-hub'), hf_xet_version=version('hf-xet'), network_routes=routes, interface_byte_deltas={dev: {direction: after[dev][direction]-before[dev][direction] for direction in ['rx','tx']} for dev in before if dev in after}, interface_counter_caveat='Host-wide traffic, including unrelated activity; counter snapshots may lag. Not an isolated per-process wire measurement.', compute_node_hostname='b40x4-07', compute_node_average_MB_per_second=prior['average_MB_per_second'], compute_node_elapsed_seconds=prior['elapsed_seconds'], speedup_vs_compute=rate/prior['average_MB_per_second'], elapsed_reduction_percent=(1-elapsed/prior['elapsed_seconds'])*100)
(root / 'Qwen3.8-27B-login1-download-metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
print('DOWNLOAD COMPLETE\n'+json.dumps(metrics, indent=2), flush=True)
