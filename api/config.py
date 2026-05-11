from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- API Configuration ---
class ApiSettings(BaseSettings):
    """Settings for API authentication."""
    api_keys: List[str] = []  # List of valid keys
    
    model_config = SettingsConfigDict(env_file="app/.env")

# --- Llama Server Configuration ---
class LlamaArgs(BaseModel):
    """Model for a single argument passed to llama-server."""
    port: int = 8080 
    host: str = "0.0.0.0"
    m: str = "/models/mistralai_Mistral-Small-3.2-24B-Instruct-2506-Q4_K_M.gguf"
    cache_type_k: str = "f16"
    cache_type_v: str = "f16"
    n_cpu_moe: int = 0
    ngl: int = 32
    no_mmap: bool = False
    mlock: bool = False
    jinja: bool = False
    ctx_size: int = 2048

    def to_command_list(self) -> List[str]:
        """Converts the Pydantic model into a list of command line arguments."""
        cmd = []
        
        # Boolean flags: add flag if True
        if self.no_mmap:
            cmd.append("--no-mmap")
        if self.mlock:
            cmd.append("--mlock")
        if self.jinja:
            cmd.append("--jinja")
            
        # String/Int flags
        if self.host:
            cmd.extend(["--host", self.host])
        if self.port > 0:
            cmd.extend(["--port", str(self.port)])
        
        if self.cache_type_k:
            cmd.extend(["--cache-type-k", self.cache_type_k])
        if self.cache_type_v:
            cmd.extend(["--cache-type-v", self.cache_type_v])
            
        if self.n_cpu_moe > 0:
            cmd.extend(["--n-cpu-moe", str(self.n_cpu_moe)])
            
        if self.ngl > 0:
            cmd.extend(["-ngl", str(self.ngl)])
            
        if self.ctx_size > 0:
            cmd.extend(["--ctx-size", str(self.ctx_size)])
            
        # Model path (-m)
        if self.m:
            cmd.extend(["-m", self.m])
            
        return cmd

class AppSettings(BaseSettings):
    """Main application settings loaded from .env"""
    # Default values for llama-server
    default_host: str = "0.0.0.0"
    default_port: int = 8080
    default_model: str = "/models/mistralai_Mistral-Small-3.2-24B-Instruct-2506-Q4_K_M.gguf"
    default_cache_type_k: str = "f16"
    default_cache_type_v: str = "f16"
    default_n_cpu_moe: int = 0
    default_ngl: int = 36
    default_no_mmap: bool = False
    default_mlock: bool = False
    default_jinja: bool = False
    default_ctx_size: int = 4096
    
    # Socket path (assuming default for standard build)
    socket_path: str = "/tmp/llama-server.sock"
    
    # API Configuration
    api_keys: str = ""

    model_config = SettingsConfigDict(env_file="app/.env")