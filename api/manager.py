import subprocess
import os
import logging
import psutil
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
            print("Server already running. Please restart first.")
            return False
        
        print("Start Server args received: ", args)

        command = ["/usr/local/bin/llama-server"] + args.to_command_list()

        logger.info(f"Starting server with: {' '.join(command)}")
        print("Starting server with: ", command)

        try:
            # Create new process
            self.process = subprocess.Popen(
                command,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
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
            logger.info("Server does not need stopping.")
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
        Checks if the server is running by searching the process list.
        Returns status info.
        """
        # Check system-wide process list for 'llama-server'
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'llama-server':
                    return {"status": "running", "message": "Llama server is running."}
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        # If no process found, check if the managed process is just starting
        if self.process and self.process.poll() is None:
            return {"status": "starting", "message": "Process is starting..."}
        
        return {"status": "stopped", "message": "Server is stopped."}