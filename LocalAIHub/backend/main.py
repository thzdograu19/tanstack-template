# backend/main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import threading
import time
import logging
import os

from model_detector import detect_models
import process_manager as pm

app = FastAPI()
logger = logging.getLogger("backend")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/backend.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

# Simple in-memory state
state = {
    "active_engine": None,  # "ollama" or "comfyui" or None
    "active_model": None,
    "last_activity": time.time()
}

IDLE_TIMEOUT_SECONDS = int(os.environ.get("IDLE_TIMEOUT_SECONDS", "0"))  # 0 = disabled

class SelectModelRequest(BaseModel):
    engine: str
    model: str

@app.get("/models")
def models():
    """
    Return detected models grouped by engine.
    """
    m = detect_models()
    return m

@app.post("/select_model")
def select_model(req: SelectModelRequest):
    """
    Switch engine based on selection.
    """
    engine = req.engine.lower()
    model = req.model
    logger.info("Select model request: %s %s", engine, model)
    state["last_activity"] = time.time()
    if engine == "ollama":
        # Start Ollama and stop ComfyUI
        try:
            pm.start_ollama()
            state["active_engine"] = "ollama"
            state["active_model"] = model
            return {"status": "ok", "active_engine": state["active_engine"], "active_model": state["active_model"]}
        except Exception as e:
            logger.exception("Failed to start Ollama")
            raise HTTPException(status_code=500, detail=str(e))
    elif engine == "comfyui":
        try:
            pm.start_comfyui()
            state["active_engine"] = "comfyui"
            state["active_model"] = model
            return {"status": "ok", "active_engine": state["active_engine"], "active_model": state["active_model"]}
        except Exception as e:
            logger.exception("Failed to start ComfyUI")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Unknown engine")

@app.get("/status")
def status():
    """
    Return current running engine and active model.
    """
    # Update running state by checking processes
    running = None
    if pm.OLLAMA_ENGINE.is_running():
        running = "ollama"
    elif pm.COMFY_ENGINE.is_running():
        running = "comfyui"
    else:
        running = None
    state["active_engine"] = running
    return {"active_engine": state["active_engine"], "active_model": state["active_model"]}

# Optional idle shutdown thread
def idle_watcher():
    while True:
        try:
            if IDLE_TIMEOUT_SECONDS > 0:
                now = time.time()
                last = state.get("last_activity", now)
                if state.get("active_engine") and (now - last) > IDLE_TIMEOUT_SECONDS:
                    logger.info("Idle timeout reached, stopping engines")
                    pm.stop_all()
                    state["active_engine"] = None
                    state["active_model"] = None
            time.sleep(5)
        except Exception:
            logger.exception("Idle watcher error")
            time.sleep(5)

if IDLE_TIMEOUT_SECONDS > 0:
    t = threading.Thread(target=idle_watcher, daemon=True)
    t.start()

if __name__ == "__main__":
    # Run uvicorn for local-only usage
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)
