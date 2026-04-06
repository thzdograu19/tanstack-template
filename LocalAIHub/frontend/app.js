const API_BASE = "http://127.0.0.1:8001";

const $ollamaList = document.getElementById("ollama-list");
const $comfyList = document.getElementById("comfy-list");
const $engine = document.getElementById("engine");
const $loading = document.getElementById("loading");

async function fetchModels() {
  try {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error("Failed to fetch models");
    const data = await res.json();
    renderModels(data);
  } catch (err) {
    console.error(err);
    $ollamaList.innerHTML = `<li class="model-item"><div class="model-name">Error fetching models</div></li>`;
    $comfyList.innerHTML = "";
  }
}

function renderModels(data) {
  $ollamaList.innerHTML = "";
  $comfyList.innerHTML = "";
  const ollama = data.ollama || [];
  const comfy = data.comfyui || [];

  if (ollama.length === 0) {
    $ollamaList.innerHTML = `<li class="model-item"><div class="model-name">No Ollama models found</div></li>`;
  } else {
    ollama.forEach(m => {
      const li = document.createElement("li");
      li.className = "model-item";
      li.innerHTML = `<div><div class="model-name">${m.name}</div><div class="model-meta">LLM</div></div>`;
      li.onclick = () => selectModel("ollama", m.name);
      $ollamaList.appendChild(li);
    });
  }

  if (comfy.length === 0) {
    $comfyList.innerHTML = `<li class="model-item"><div class="model-name">No ComfyUI models found</div></li>`;
  } else {
    comfy.forEach(m => {
      const li = document.createElement("li");
      li.className = "model-item";
      li.innerHTML = `<div><div class="model-name">${m.file}</div><div class="model-meta">${m.type}</div></div>`;
      li.onclick = () => selectModel("comfyui", m.file);
      $comfyList.appendChild(li);
    });
  }
}

async function selectModel(engine, model) {
  showLoading(true);
  try {
    const res = await fetch(`${API_BASE}/select_model`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({engine, model})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to select model");
    $engine.textContent = data.active_engine || "idle";
  } catch (err) {
    console.error(err);
    alert("Failed to switch engine: " + err.message);
  } finally {
    showLoading(false);
  }
}

function showLoading(on) {
  if (on) {
    $loading.classList.remove("hidden");
  } else {
    $loading.classList.add("hidden");
  }
}

async function refreshStatus() {
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) return;
    const data = await res.json();
    $engine.textContent = data.active_engine || "idle";
  } catch (e) {
    $engine.textContent = "offline";
  }
}

async function init() {
  showLoading(true);
  await fetchModels();
  await refreshStatus();
  showLoading(false);
}

window.addEventListener("load", init);
