import subprocess
import time
import os
import logging
from typing import Optional
from config import AppSettings, LlamaArgs

logger = logging.getLogger(__name__)

class LlamaProcessManager:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.process: Optional[subprocess.Popen] = None
        self.socket_path = settings.socket_path

    def start_server(self, args: LlamaArgs):
        """Starts the llama-server subprocess with the given arguments."""
        if self.process and self.process.poll() is None:
            logger.warning("Server already running. Please restart first.")
            return False

        # Cleanup stale socket file before starting
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
                logger.info(f"Removed stale socket: {self.socket_path}")
            except OSError as e:
                logger.warning(f"Could not remove socket: {e}")

        command = ["llama-server"] + args.to_command_list()
        
        logger.info(f"Starting server with: {' '.join(command)}")
        
        try:
            # Create new process
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("Server process started.")
            return True
        except FileNotFoundError:
            logger.error("llama-server binary not found.")
            return False
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False

    def stop_server(self):
        """Stops the subprocess gracefully."""
        if not self.process:
            return

        logger.info("Stopping server...")
        
        # Terminate gracefully (SIGTERM)
        self.process.terminate()
        
        # Wait for process to finish (timeout 5 seconds)
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Server did not terminate gracefully, killing...")
            self.process.kill()
            self.process.wait()
            
        self.process = None
        
        # Cleanup socket file
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except OSError:
                pass

    def check_health(self) -> dict:
        """
        Checks if the server is running and listening on the socket.
        Returns status info.
        """
        if self.process and self.process.poll() is None:
            # Process is alive
            if os.path.exists(self.socket_path):
                return {"status": "running", "message": "Llama server is healthy and listening."}
            else:
                return {"status": "starting", "message": "Process is alive, waiting for socket file..."}
        else:
            return {"status": "stopped", "message": "Server is stopped."}