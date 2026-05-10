## Code Structure Design

To separate concerns and ensure maintainability, we will split the application into three files:

config.py: Handles configuration settings using pydantic-settings.
manager.py: Manages the lifecycle of the llama-server subprocess.
main.py: The FastAPI application with endpoints and startup logic.

### Code Review:

* Auth: Handles optional API key via Header. If .env is empty, validation is skipped.
* Restart: Uses LlamaArgs to capture new variables. stop_server cleans up socket file.  start_server creates new process.
* Status: Polls socket file existence.
* Dependencies: Correct modules imported.
* Startup: @app.on_event("startup") ensures the server starts automatically on container boot.

### Codebase Layout:

project-root/
├── docker/
│   ├── Dockerfile
│   └── .env
├── api/
│   ├── main.py         # FastAPI application
│   ├── config.py       # Pydantic settings
│   └── service.py      # Subprocess logic
└── requirements.txt


