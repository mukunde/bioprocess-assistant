"""Start the Windows graph chat with a private, loopback-only Ollama process."""
import argparse
import ctypes
from ctypes import wintypes
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

from graph_chat_ministral import HYBRID_GPU_LAYERS, MODEL
from tools import load_graph_dotenv, query_graph


ROOT = Path(__file__).resolve().parent
MIN_AVAILABLE_MIB = 1024
PROFILES = {"cpu": "CPU", "hybrid": "Hybrid", "irisxe": "IrisXe"}


class StartupError(RuntimeError):
    pass


def request(port, path, payload=None, timeout=3):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        if payload is None:
            connection.request("GET", path)
        else:
            connection.request("POST", path, json.dumps(payload), {"Content-Type": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            raise StartupError(f"Local {path} returned HTTP {response.status}.")
        return json.load(response) if path.startswith("/api/") else None
    finally:
        connection.close()


def wait_ready(process, port, path, service):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise StartupError(f"{service} exited during startup.")
        try:
            request(port, path)
            if process.poll() is None:
                return
        except (OSError, http.client.HTTPException, StartupError):
            time.sleep(0.5)
    raise StartupError(f"{service} did not become ready on port {port}.")


def require_free_port(port):
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            raise StartupError(f"Port {port} is occupied. Choose another port.") from None


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.DWORD), ("load", wintypes.DWORD),
        ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong), ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    ]


def check_memory(profile, phase):
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise StartupError("Windows could not report available physical memory.")
    available = status.available_physical // (1024 * 1024)
    print(f"{phase}: {available:,} MiB RAM available.", flush=True)
    if available < MIN_AVAILABLE_MIB:
        remedy = " Relaunch with -Profile CPU." if profile != "CPU" else " Free RAM and retry."
        raise StartupError(f"Startup requires {MIN_AVAILABLE_MIB:,} MiB available RAM.{remedy}")


def check_graph():
    load_graph_dotenv(ROOT / ".env")
    required = (
        "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "NEO4J_DATABASE",
        "CHAINLIT_AUTH_SECRET", "DEMO_USERNAME", "DEMO_PASSWORD",
    )
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        raise StartupError(f"Set the local configuration in .env: {', '.join(missing)}.")
    uri = urlsplit(os.environ["NEO4J_URI"])
    if uri.scheme != "bolt" or uri.hostname not in {"127.0.0.1", "::1", "localhost"}:
        raise StartupError("Configure a direct loopback Bolt address in NEO4J_URI.")
    try:
        match = query_graph("high column pressure")
    except Exception:
        raise StartupError("Neo4j check failed. Verify the local server, credentials, and graph seed.") from None
    if not match["found"] or match["symptom"]["name"] != "High column pressure":
        raise StartupError("The local graph seed is missing. Run scripts/load_graph.py.")


def ollama_environment(profile, port):
    environment = os.environ.copy()
    enable_gpu = "0" if profile == "CPU" else "1"
    environment.update(
        OLLAMA_HOST=f"127.0.0.1:{port}",
        OLLAMA_NO_CLOUD="1", OLLAMA_NOHISTORY="1", OLLAMA_NOPRUNE="1",
        OLLAMA_MAX_LOADED_MODELS="1", OLLAMA_NUM_PARALLEL="1",
        OLLAMA_IGPU_ENABLE=enable_gpu, OLLAMA_VULKAN=enable_gpu,
        CUDA_VISIBLE_DEVICES="-1", ROCR_VISIBLE_DEVICES="-1", HIP_VISIBLE_DEVICES="-1",
        OLLAMA_DEBUG="INFO",
    )
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "NEO4J_PASSWORD",
                "CHAINLIT_AUTH_SECRET", "DEMO_USERNAME", "DEMO_PASSWORD"):
        environment.pop(key, None)
    return environment


def load_model(args, log_path):
    try:
        request(args.ollama_port, "/api/show", {"model": MODEL})
    except StartupError:
        raise StartupError(f"Install the local model {MODEL} as described in the setup guide.") from None
    options = {"num_ctx": 4096}
    if args.profile == "Hybrid":
        options["num_gpu"] = HYBRID_GPU_LAYERS
    request(args.ollama_port, "/api/generate", {
        "model": MODEL,
        "stream": False,
        "keep_alive": "15m",
        "options": options,
    }, timeout=180)
    resident = request(args.ollama_port, "/api/ps")["models"]
    loaded = next((entry for entry in resident if entry.get("name") == MODEL), None)
    vram = loaded.get("size_vram") if loaded else None
    if args.profile == "CPU" and vram != 0:
        raise StartupError("Ollama did not confirm CPU-only residency.")
    if args.profile != "CPU":
        log = log_path.read_text(encoding="utf-8", errors="replace")
        offload = re.search(r"offloaded (\d+)/(\d+) layers to GPU", log)
        iris = re.search(r"using device Vulkan\d+ \(Intel.*Iris.*Xe", log, re.IGNORECASE)
        count, total = map(int, offload.groups()) if offload else (0, 0)
        if args.profile == "Hybrid":
            if not (iris and vram and vram < loaded.get("size", 0) and count == HYBRID_GPU_LAYERS < total):
                raise StartupError(
                    f"Hybrid offload of {HYBRID_GPU_LAYERS} layers to Intel Iris Xe could not be verified. "
                    "Relaunch with -Profile CPU."
                )
            print(f"Hybrid placement verified: {count}/{total} layers on Iris Xe.", flush=True)
        elif not (vram and iris and count > 0 and count == total):
            raise StartupError("Full offload to Intel Iris Xe could not be verified. Relaunch with -Profile CPU.")
    print(f"Ministral loaded on {args.profile} (Ollama GPU allocation {vram} bytes).", flush=True)


def stop_process(process):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def run(args):
    ollama_executable = shutil.which("ollama")
    if not ollama_executable:
        raise StartupError("Install Ollama and put it on PATH.")
    if args.port == args.ollama_port:
        raise StartupError("Chainlit and Ollama require different ports.")
    for port in (args.port, args.ollama_port):
        require_free_port(port)
    check_graph()

    log_path = Path(tempfile.mkdtemp(prefix="bp-local-graph-")) / "ollama.log"
    print(f"Ollama log: {log_path}", flush=True)
    ollama = chainlit = None
    server_ready = False
    try:
        with log_path.open("w", encoding="utf-8") as log:
            ollama = subprocess.Popen([ollama_executable, "serve"], cwd=ROOT, stdout=log,
                                      stderr=subprocess.STDOUT, env=ollama_environment(args.profile, args.ollama_port),
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        wait_ready(ollama, args.ollama_port, "/api/version", "Ollama")
        server_ready = True
        load_model(args, log_path)
        check_memory(args.profile, "After model load")
        environment = os.environ.copy()
        environment.update(
            BIOPROCESS_MODE="graph", BIOPROCESS_GRAPH_BACKEND="ministral",
            BIOPROCESS_LOCAL_OLLAMA_PORT=str(args.ollama_port), BIOPROCESS_GRAPH_CHAT_TRACE="0",
            BIOPROCESS_LOCAL_OLLAMA_PROFILE=args.profile,
            ANTHROPIC_API_KEY="", ANTHROPIC_AUTH_TOKEN="",
        )
        chainlit = subprocess.Popen(
            [sys.executable, "-B", "-m", "chainlit", "run", "app.py",
             "--host", "127.0.0.1", "--port", str(args.port), "--headless"],
            cwd=ROOT, env=environment, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        wait_ready(chainlit, args.port, "/", "Chainlit")
        check_memory(args.profile, "Neo4j, Ollama, and Chainlit ready")
        print(f"Local graph chat ready at http://127.0.0.1:{args.port}/", flush=True)
        if args.check_only:
            return 0
        # A Windows process wait without a timeout can defer Ctrl+C.
        while chainlit.poll() is None:
            time.sleep(0.25)
        return chainlit.returncode
    finally:
        try:
            stop_process(chainlit)
        finally:
            try:
                if server_ready and ollama.poll() is None:
                    request(args.ollama_port, "/api/generate",
                            {"model": MODEL, "keep_alive": 0, "stream": False}, timeout=15)
            except (OSError, http.client.HTTPException, StartupError, KeyboardInterrupt):
                pass
            finally:
                stop_process(ollama)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=str.casefold, choices=tuple(PROFILES), default="cpu")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ollama-port", type=int, default=11435)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("This launcher requires Windows.")
    if not all(1024 <= port <= 65535 for port in (args.port, args.ollama_port)):
        parser.error("Ports must be between 1024 and 65535.")
    args.profile = PROFILES[args.profile]
    signal.signal(signal.SIGBREAK, signal.getsignal(signal.SIGINT))
    try:
        return run(args)
    except KeyboardInterrupt:
        return 130
    except (OSError, http.client.HTTPException, StartupError, ValueError) as error:
        print(f"Local graph chat startup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
