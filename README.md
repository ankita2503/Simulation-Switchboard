
# Simulation Switchboard

The task at hand is to develop the Danfoss Switchboard API that efficiently manages computational
simulation resources in Danfoss. The API will handle the spawning and monitoring of Docker containers
for incoming simulation jobs, allowing each job to be executed in its own container. This containerised
approach allows for better resource management and scaling of simulations.




## Run Locally

#### Clone the project

```bash
  git clone https://github.com/ankita2503/Simulation-Switchboard.git 
```

#### Go to the project directory

```bash
  cd Simulation-Switchboard
```

#### Install dependencies

```bash
  pip install requirements.txt
```

#### Start the server

```bash
  python3 main.py
```

#### Access and run API in browser using swagger endpoint

```bash
  http://127.0.0.1:5000/swagger/
```

#### Import Postman Collection and test APIs in postman

```bash
  cd collection
  import Computation.postman_collection.json in Postman
```
## API Reference

#### 1. Endpoint to handle incoming computational requests and spawn a new container based on the incoming request data and bind mount a storage volume

```http
  POST /computation
```


#### Sample Body 


        {
            "image":"ankita2503/compute-random-date:V0.1",
            "env_vars":"test",
            "input_data":"ComputationResult"
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



## Appendix

### To Deactivate the default venv and create new env :

#### Run following:

```bash
deactivate 

python3 -m venv simEnv

source simEnv/bin/activate

pip install -U pip

pip install docker

pip install flask

pip freeze > requirements.txt
```
