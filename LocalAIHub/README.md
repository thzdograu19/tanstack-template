# Local AI Hub

Minimal, fast, and beautiful desktop controller for local AI tools. Let the user pick a model; the app automatically starts the correct engine (Ollama or ComfyUI) and ensures only one engine runs at a time.

## Supported Engines

- **Ollama** for LLMs (Qwen, Llama, Mistral, etc.)
- **ComfyUI** for image/video models (SDXL, LTX Video, etc.)

## Project Structure

```
LocalAIHub/
├─ backend/
│  ├─ main.py              # FastAPI server
│  ├─ process_manager.py   # Engine process control
│  ├─ model_detector.py    # Model detection logic
│  ├─ requirements.txt     # Python dependencies
│  └─ logs/                # Log files
├─ frontend/
│  ├─ index.html           # Main HTML file
│  ├─ app.js               # Frontend JavaScript
│  └─ styles.css           # Dark theme CSS
├─ build_helpers/
│  ├─ check_and_install_deps.bat  # Windows setup script
│  └─ build_backend.bat           # Windows build script
└─ README.md
```

## Core Features

### Model Detection
- Runs `ollama list` to detect Ollama models
- Scans `/ComfyUI/models` for `.safetensors` and `.ckpt` files
- Returns only relevant model names and file types

### Model-Based Routing
- User selects a model (not a mode)
- If model is Ollama → start Ollama, stop ComfyUI
- If model is ComfyUI → start ComfyUI, stop Ollama

### Process Manager
- `start_ollama()`, `stop_ollama()`, `start_comfyui()`, `stop_comfyui()`
- Uses subprocess with proper process groups and cleanup
- Ensures only one engine runs at a time

### Backend API (FastAPI)
- `GET /models` → detected models
- `POST /select_model` → select model and switch engine
- `GET /status` → current running engine and active model

### Frontend (Tauri-ready)
- Minimal dark UI
- Model list grouped by engine
- Click to select
- Shows status and loading indicator

## Installation

### Prerequisites

1. **Python 3.10+** - Ensure it's on your PATH
2. **Ollama** (optional) - Install from [ollama.ai](https://ollama.ai)
3. **ComfyUI** (optional) - Install from [GitHub](https://github.com/comfyanonymous/ComfyUI)

### Quick Setup (Windows)

1. Run the setup script:
   ```batch
   build_helpers\check_and_install_deps.bat
   ```

2. Activate the virtual environment:
   ```batch
   call venv\Scripts\activate
   ```

3. Start the backend:
   ```batch
   python backend\main.py
   ```

4. Open `frontend/index.html` in your browser, or use Tauri for a native app.

### Manual Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Start the backend:
   ```bash
   python backend/main.py
   ```

5. The API will be available at `http://127.0.0.1:8001`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COMFY_MODELS_DIR` | Path to ComfyUI models folder | `C:\ComfyUI\models` |
| `COMFYUI_DIR` | Path to ComfyUI installation | `C:\ComfyUI` |
| `PYTHON_EXE` | Python executable for ComfyUI | `python` |
| `IDLE_TIMEOUT_SECONDS` | Auto-shutdown after idle (0 = disabled) | `0` |

### Example (.env)

```bash
COMFY_MODELS_DIR=/path/to/ComfyUI/models
COMFYUI_DIR=/path/to/ComfyUI
IDLE_TIMEOUT_SECONDS=300
```

## API Reference

### GET /models

Returns detected models grouped by engine.

**Response:**
```json
{
  "ollama": [
    {"name": "llama2", "type": "llm"},
    {"name": "mistral", "type": "llm"}
  ],
  "comfyui": [
    {"file": "sd_xl_base.safetensors", "path": "/path/to/file", "type": "image"}
  ]
}
```

### POST /select_model

Select a model and start the corresponding engine.

**Request:**
```json
{
  "engine": "ollama",
  "model": "llama2"
}
```

**Response:**
```json
{
  "status": "ok",
  "active_engine": "ollama",
  "active_model": "llama2"
}
```

### GET /status

Get current running engine and active model.

**Response:**
```json
{
  "active_engine": "ollama",
  "active_model": "llama2"
}
```

## Using with Tauri

Tauri is recommended for building a native desktop application.

### Setup

1. Install Node.js and Rust toolchain
2. Create a Tauri project:
   ```bash
   npm create tauri-app@latest
   ```
3. Copy `frontend/*` into your Tauri project's source directory
4. Configure `tauri.conf.json` to include the backend executable

### Development

1. Start the backend:
   ```bash
   python backend/main.py
   ```

2. Start Tauri dev server:
   ```bash
   npm run tauri dev
   ```

### Production Build

1. Build the backend executable:
   ```batch
   build_helpers\build_backend.bat
   ```

2. Configure Tauri to bundle the backend in `tauri.conf.json`:
   ```json
   {
     "bundle": {
       "resources": ["../dist/LocalAIHubBackend.exe"]
     }
   }
   ```

3. Build the Tauri app:
   ```bash
   npm run tauri build
   ```

## Building Standalone Backend

To create a single-file executable:

```batch
build_helpers\build_backend.bat
```

The executable will be in `dist/LocalAIHubBackend.exe`.

## Troubleshooting

### Ollama not found
Ensure Ollama is installed and `ollama` command is on your PATH.

### ComfyUI not found
Set the `COMFYUI_DIR` environment variable to your ComfyUI installation path.

### Port already in use
Change the port in `backend/main.py`:
```python
uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=False)
```

### Process cleanup issues
Check `backend/logs/process_manager.log` for process management details.

## Optional Enhancements

- **Idle Auto-Shutdown**: Set `IDLE_TIMEOUT_SECONDS` to enable
- **Logging**: Check `backend/logs/` for detailed logs
- **Model Tags**: Extend `model_detector.py` to add heuristic tags
- **Health Checks**: Add `/health` endpoint for monitoring

## Best Practices

1. Keep the backend minimal - it only controls external services
2. Test switching repeatedly to ensure proper cleanup
3. For production, sign the Windows executable
4. Use environment variables for custom paths
5. Monitor logs for debugging

## License

MIT License - See LICENSE file for details.
