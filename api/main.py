import time
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import your modules (assumed to be in the same directory)
from config import AppSettings, LlamaArgs
from manager import LlamaProcessManager

# 1. Define the lifespan context manager
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup Logic: Initialize settings and manager
    app_settings = AppSettings()
    manager = LlamaProcessManager(app_settings)
    
    # Initialize defaults
    default_args = LlamaArgs(
        m=app_settings.default_model,
        cache_type_k=app_settings.default_cache_type_k,
        cache_type_v=app_settings.default_cache_type_v,
        n_cpu_moe=app_settings.default_n_cpu_moe,
        ngl=app_settings.default_ngl,
        no_mmap=app_settings.default_no_mmap,
        mlock=app_settings.default_mlock,
        jinja=app_settings.default_jinja,
        context=app_settings.default_context
    )
    
    success = manager.start_server(default_args)
    if not success:
        print("Failed to start default server.")

    yield # Yield control to the application (runs while API is active)

    # Optional: Shutdown logic
    # manager.stop_server()

# 2. Initialize FastAPI with the lifespan parameter
app = FastAPI(
    title="Llama Server Manager", 
    lifespan=app_lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "API Service is Running"}

@app.post("/restartllama")
def restart_llama(new_args: LlamaArgs, x_api_key: Optional[str] = Header(None)):
    """
    Restarts the llama-server process with new parameters.
    """
    app_settings = AppSettings()
    # Authentication
    valid_keys = app_settings.api_keys
    if valid_keys:
        # If keys exist, check header. If missing or wrong, deny.
        if not x_api_key or x_api_key not in valid_keys.split(","):
            raise HTTPException(status_code=401, detail="Invalid API Key")

    # Logic: Stop old, Start new [2]
    manager.stop_server()
    
    # Give a brief moment for socket cleanup
    time.sleep(1)
    
    # Start new with provided overrides [2]
    success = manager.start_server(new_args)
    
    if success:
        return {"status": "restarting", "message": "Process restarting with new parameters."}
    else:
        raise HTTPException(status_code=500, detail="Failed to start server.")

@app.get("/restart-status")
def restart_status(x_api_key: Optional[str] = Header(None)):
    """
    Monitors the restart process.
    """
    app_settings = AppSettings()
    # Authentication
    valid_keys = app_settings.api_keys
    if valid_keys:
        if not x_api_key or x_api_key not in valid_keys.split(","):
            raise HTTPException(status_code=401, detail="Invalid API Key")

    # Check health [2]
    health = manager.check_health()
    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)