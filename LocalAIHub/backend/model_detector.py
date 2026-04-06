# backend/model_detector.py
import os
import subprocess
import json
from typing import List, Dict, Any

COMFY_MODELS_DIR = os.environ.get("COMFY_MODELS_DIR", os.path.expanduser(r"C:\ComfyUI\models"))

def detect_ollama_models() -> List[str]:
    """
    Run `ollama list` and parse model names.
    Returns list of model names (strings).
    """
    try:
        proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False)
        out = proc.stdout.strip()
        models = []
        # Ollama prints a table or JSON depending on version; try JSON first
        try:
            parsed = json.loads(out)
            # If JSON is a list of dicts with 'name'
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "name" in item:
                        models.append(item["name"])
        except Exception:
            # Fallback: parse lines, skip headers
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                # skip header lines that contain "NAME" or "MODEL"
                if line.lower().startswith("name") or "model" in line.lower():
                    continue
                # take first token as model name
                parts = line.split()
                if parts:
                    models.append(parts[0])
    except FileNotFoundError:
        models = []
    return models

def detect_comfyui_models() -> List[Dict[str, Any]]:
    """
    Scan COMFY_MODELS_DIR for .safetensors and .ckpt files.
    Returns list of dicts: { "file": filename, "path": fullpath, "type": "safetensors"|"ckpt" }
    """
    results = []
    try:
        for root, _, files in os.walk(COMFY_MODELS_DIR):
            for f in files:
                if f.lower().endswith(".safetensors"):
                    results.append({"file": f, "path": os.path.join(root, f), "type": "safetensors"})
                elif f.lower().endswith(".ckpt"):
                    results.append({"file": f, "path": os.path.join(root, f), "type": "ckpt"})
    except Exception:
        results = []
    return results

def detect_models() -> Dict[str, Any]:
    """
    Return combined model list with categories.
    """
    ollama = detect_ollama_models()
    comfy = detect_comfyui_models()
    return {
        "ollama": [{"name": m, "type": "llm"} for m in ollama],
        "comfyui": [{"file": c["file"], "path": c["path"], "type": "image"} for c in comfy]
    }
