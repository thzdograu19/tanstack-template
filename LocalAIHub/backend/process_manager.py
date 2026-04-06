# backend/process_manager.py
import subprocess
import os
import signal
import time
from typing import Optional
import threading
import logging

logger = logging.getLogger("process_manager")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/process_manager.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

class EngineProcess:
    def __init__(self):
        self.proc: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def start(self, cmd, cwd=None, env=None):
        with self.lock:
            if self.is_running():
                logger.info("Process already running, skipping start")
                return
            logger.info(f"Starting process: {cmd}")
            # Start in new process group for easier termination
            self.proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False,
                creationflags=(0x00000200) if os.name == "nt" else 0
            )
            time.sleep(0.5)

    def stop(self, timeout=5):
        with self.lock:
            if not self.proc:
                logger.info("No process to stop")
                return
            if self.proc.poll() is not None:
                logger.info("Process already exited")
                self.proc = None
                return
            logger.info("Stopping process")
            try:
                if os.name == "nt":
                    self.proc.terminate()
                else:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                start = time.time()
                while time.time() - start < timeout:
                    if self.proc.poll() is not None:
                        break
                    time.sleep(0.2)
                if self.proc.poll() is None:
                    logger.info("Killing process")
                    if os.name == "nt":
                        self.proc.kill()
                    else:
                        os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
            except Exception as e:
                logger.exception("Error stopping process: %s", e)
            finally:
                self.proc = None

OLLAMA_ENGINE = EngineProcess()
COMFY_ENGINE = EngineProcess()

def start_ollama():
    """
    Start Ollama server if not running.
    Adjust command as needed for your Ollama installation.
    """
    # Example: `ollama serve` or `ollama daemon` depending on version
    if OLLAMA_ENGINE.is_running():
        logger.info("Ollama already running")
        return
    # Stop ComfyUI first
    stop_comfyui()
    cmd = ["ollama", "serve"]
    try:
        OLLAMA_ENGINE.start(cmd)
        logger.info("Ollama started")
    except FileNotFoundError:
        logger.exception("Ollama executable not found")

def stop_ollama():
    OLLAMA_ENGINE.stop()

def start_comfyui(comfy_dir=None):
    """
    Start ComfyUI. Adjust command to your ComfyUI startup script.
    Example: python main.py or python launch.py
    """
    if COMFY_ENGINE.is_running():
        logger.info("ComfyUI already running")
        return
    # Stop Ollama first
    stop_ollama()
    comfy_dir = comfy_dir or os.environ.get("COMFYUI_DIR", os.path.expanduser(r"C:\ComfyUI"))
    # Common start command: python main.py or python launch.py
    python_exe = os.environ.get("PYTHON_EXE", "python")
    # Prefer a launch script if present
    launch_script = None
    for candidate in ("launch.py", "main.py", "server.py"):
        p = os.path.join(comfy_dir, candidate)
        if os.path.exists(p):
            launch_script = p
            break
    if launch_script:
        cmd = [python_exe, launch_script]
    else:
        # fallback: try to run comfyui via module
        cmd = [python_exe, "-m", "ComfyUI"]
    try:
        COMFY_ENGINE.start(cmd, cwd=comfy_dir)
        logger.info("ComfyUI started")
    except FileNotFoundError:
        logger.exception("Python executable not found")

def stop_comfyui():
    COMFY_ENGINE.stop()

def stop_all():
    stop_ollama()
    stop_comfyui()
