from fastapi import FastAPI, HTTPException, Header
from typing import Optional
import uvicorn
from config import AppSettings, LlamaArgs
from manager import LlamaProcessManager
from auth import verify_api_key

# Initialize settings and manager
app_settings = AppSettings()
manager = LlamaProcessManager(app_settings)

app = FastAPI(title="Llama Server Manager")

# Add startup event to launch the server
@app.on_event("startup")
def startup_event():
    """Starts the llama-server process on application startup."""
    # Construct default arguments from settings
    default_args = LlamaArgs(
        m=app_settings.default_model,
        host=app_settings.default_host,
        port=app_settings.default_port,
        cache_type_k=app_settings.default_cache_type_k,
        cache_type_v=app_settings.default_cache_type_v,
        n_cpu_moe=app_settings.default_n_cpu_moe,
        ngl=app_settings.default_ngl,
        no_mmap=app_settings.default_no_mmap,
        mlock=app_settings.default_mlock,
        jinja=app_settings.default_jinja,
        ctx_size=app_settings.default_ctx_size
    )
    
    # Start the process
    success = manager.start_server(default_args)
    if success:
        print("Llama server started successfully.")
    else:
        print("Failed to start llama server.")


@app.get("/restart-status")
def restart_status(x_api_key: Optional[str] = Header(None)):
    """
    Monitors the restart process.
    """
    verify_api_key(app_settings, x_api_key)
    # The logic for checking health status
    health = manager.check_health()
    return health

@app.get("/health")
def health_check():
    return {"status": "API Service is Running"}

@app.post("/restart-llama")
def restart_llama(new_args: LlamaArgs, x_api_key: Optional[str] = Header(None)):
    """
    Restarts the llama-server process with new parameters.
    """
    verify_api_key(app_settings, x_api_key)
    
    # Logic for stopping and starting the process
    manager.stop_server()
    
    # Give a brief moment for socket cleanup
    import time
    time.sleep(1)
    
    print("New Arguments received", new_args)

    # Start new with provided overrides
    success = manager.start_server(new_args)
    
    if success:
        return {"status": "restarting", "message": "Process restarting with new parameters."}
    else:
        raise HTTPException(status_code=500, detail="Failed to start server.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)