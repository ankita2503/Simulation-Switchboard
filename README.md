
# Simulation Switchboard

The project is to develop the APIs that efficiently manages computational
simulation resources. The API will handle the spawning and monitoring of Docker containers
for incoming simulation jobs, allowing each job to be executed in its own container. This containerised
approach allows for better resource management and scaling of simulations.




## Run Locally

### To create new env :

#### Run following:

```bash
deactivate 

python3 -m venv simEnv

source simEnv/bin/activate

pip install -U pip

pip install -r requirements.txt
```


#### Clone the project

```bash
  git clone https://github.com/ankita2503/Simulation-Switchboard.git 
```

#### Go to the project directory

```bash
  cd Simulation-Switchboard
```

#### Install dependencies (Optional)

```bash
  pip install -r requirements.txt
```

#### Start the server

```bash
  python3 main.py
```

#### Access and run API in browser using swagger endpoint

```bash
  http://127.0.0.1:5000/swagger/
```

#### Import Postman Collection and test APIs in postman (Optional)

```bash
  cd collection
  import Computation.postman_collection.json in Postman
```

#### prerequisite

```bash
  - Docker Daemon on the host
  - python 
```
## API Reference

#### 1. Endpoint to handle incoming computational requests and spawn a new container based on the incoming request data and bind mount a storage volume

```http
  POST /computation
```


#### Sample Body 


        {
        "image": "ankita2503/compute-random-date:V0.1",
        "env_vars": 
        {
            "env": "dev"
        },
        "input_data": 
        {
            "resultFolder": "computationResult",
            "containerVolumePath": "/data"
        }
        }

#### Sample Response 

        {
            "containers": 
            [
                {
                "id": "60234d60be8403a5131bb756680642abe2c43b6f9b8b75b6c7a8b22aa2b2cf93",
                "status": "running"
                }
            ]
        }
    

#### 2. Endpoint to DELETE the container with ID

```http
  DELETE /containers/{container_id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `container_id`      | `string` | **Required**. ContainerID of the container to be deleted |


#### Success Response :
    {
        "status": "success"
    }

#### 3. Endpoint to monitor container status

```http
  GET /containers
```

#### Sample Response 

        {
            "containers": 
            [
                {
                "id": "60234d60be8403a5131bb756680642abe2c43b6f9b8b75b6c7a8b22aa2b2cf93",
                "status": "running"
                }
            ]
        }

#### 3. Endpoint to monitor application health

```http
  GET /health
```

#### Sample Response 

        Health Check OK : Application is running



## Contributers
- Ankita Singh
