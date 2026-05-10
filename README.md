### W.I.P
#### This project is not finished and is currently undergoing development and testing.  Use at your own risk.

## Easy Llama (Llama-cpp, Turbo Quant, Docker with easy restart api)

### Overview:
An easy docker based setup for Llama.cpp with TurboQuant and an api for restarting llama-server.

Using http calls you can set llama.cpp startup options and restart llama-server without restarting the container.

#### This implementation is _not_ for Production use.  It is not hardened or exploit tested. Do not use it for anything othere than private testing.

#### Note: This setup is utilising CUDA for Nvidia GPUs.  Other GPUs AI frameworks are not included as I only have a NVidia card to work with. 

### Technology Used
* Docker
* Ubuntu24.04
* Cuda:12.8.1
* Python3
* llama.cpp with turboquant (Forked from: [llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant))

### Basic instructions

#### Setup

* Clone this repository to a Linux server
* cd llama-cpp-tq-docker-easyllama
* Copy ./docker/dot-env-example ./docker/.env
* If using authentication (default) then generate an APIKey.
  * A quick and easy way to generate an APIKey in Linux "openssl rand -hex 32"
* Edit ./docker/.env and set any enivronment variables on startup.
* Set your API key(s) to enable API authentication.

#### Build the image (from scratch, remove  --no-cache for updating the build)
docker build  --no-cache -t easy-llama -f ./docker/Dockerfile .

### Creating and Running a Container

#### Start a container based on the image
* [Ext port] = Port number to connect to the container on
* [Ext volume] = Docker volume name or physical volume path

docker run -d --name easy-llama --gpus all -p [Ext port]:8000 -v [Ext volume]:/models easy-llama

#### Stopping the container
docker stop easy-llama

#### Deleting the container (ready for a new start with different parameters - see Run the image).
docker container rm easy-llama

### Calling the available endpoints:

### GET /health:
#### To verify the API service is running, you can call this endpoint without authentication (if keys are not configured):

curl http://localhost:8000/health

### GET /restart-status:
#### To monitor the restart progress of the subprocess, you must include the optional X-API-Key header if valid keys are defined in the .env file:

curl http://localhost:8000/restart-status -H "X-API-Key: your_api_key"

### POST /restartllama:

#### To restart the llama-server process with new parameters, you must provide a JSON payload. The X-API-Key header is required if the server-side keys are configured in the environment file (.env).

curl -X POST http://localhost:8000/restartllama \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
    "ngl": 36,
    "context": 4096,
    "no_mmap": false
}'

### llama-server commandline parameters available.

#### Put these in the -d '{}' section of the api call to set them and restart llama-server process.

"m": "/models/[model name]"
"ngl": 36
"nn-cpu-moegl": 0
"cache-type-k": turbo3
"cache-type-v": turbo4
"no-mmap": [true/false]
"mlock": [true/false]
"jinja": [true/false]
"context": 4096

### Perminently change the llama-server startup parameters.

#### Start the container and link ./docker/.env into the container after setting the values.
docker run -d --name easy-llama --gpus all -p [Ext port]:8000 -v [Ext volume]:/models -v ./docker/.env:/app/.env:ro easy-llama

#### Edit in the API code (correct option).
Ammend ./api/config.py
Set the default values for each of the options you wish to change.
Delete the original image (if one exists).
Rebuild a new image.

#### Edit in the API code (possible but not recommended).
Alternatively, edit ./app/config.py and link the editied version back in to the container.
-v ./api/config.py:/app/config.py:ro

### Access the llama-server process as normal.