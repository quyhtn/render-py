
import os
import platform
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import psutil
from fastapi import FastAPI

app = FastAPI(title="Python CPU Lab")


def get_cpu_quota():
    # Read CPU quota from Linux cgroup v2, if available.
    path = Path("/sys/fs/cgroup/cpu.max")

    if not path.exists():
        return None

    try:
        quota, period = path.read_text().split()

        if quota == "max":
            return None

        return round(int(quota) / int(period), 2)
    except (OSError, ValueError, ZeroDivisionError):
        return None


@app.get("/")
def home():
    return {"message": "Python CPU Lab is running"}


@app.get("/system")
def system_info():
    process = psutil.Process()

    return {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "pid": os.getpid(),
        "physical_cores_visible": psutil.cpu_count(logical=False),
        "logical_cpus_visible": os.cpu_count(),
        "cpu_quota_cores": get_cpu_quota(),
        "process_threads": process.num_threads(),
        "process_memory_mb": round(
            process.memory_info().rss / 1024**2, 2
        ),
    }


def simulate_download(name):
    time.sleep(1)
    return f"Downloaded {name}"


@app.get("/io-demo")
def io_demo():
    files = ["A.pdf", "B.pdf", "C.pdf"]

    start = time.perf_counter()

    for name in files:
        simulate_download(name)

    sequential = time.perf_counter() - start

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(simulate_download, files))

    threaded = time.perf_counter() - start

    return {
        "sequential_seconds": round(sequential, 2),
        "threaded_seconds": round(threaded, 2),
        "results": results,
    }



@app.get("/thread-demo")
def thread_demo():
    def worker(name):
        pid = os.getpid()
        tid = threading.get_native_id()

        time.sleep(2)

        return {
            "name": name,
            "pid": pid,
            "thread_id": tid,
        }

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(
            pool.map(worker, ["A", "B", "C"])
        )

    return {"results": results}
