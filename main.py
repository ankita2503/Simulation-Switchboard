import asyncio
import os
import docker
from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

@app.route('/static/<path:path>')
def sendStatic(path):
    return send_from_directory('static', path)


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "SwitchBoardSimulator"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


def check_health():
    """
    This function is used to check the health of the application.
    :return: A string message indicating the health of the application.
    """
    return "Health Check OK : Application is running"


async def checkContainerStatus(container):
    """
    This function is used to test the status of the container.
    If the container is exited, then the exit code is checked.
    If the exit code is 0, then the computation is finished successfully.
    If the exit code is not 0, then the computation is finished with error.
    """
    container.wait()
    if container.status == 'exited':
        exit_code = container.attrs['State']['ExitCode']
        if exit_code == 0:
            print("Computation finished successfully")
        else:
            print("Computation finished with error, exit code:", exit_code)



async def testMountFile(container,path):
    """
    This function is used to test if the file is created in the mounted directory.
    If the file is created, the container is stopped and removed.

    Parameters
    ----------
    container : docker.models.containers.Container
        The container object.
    path : str
        The path to the file to be tested.

    Returns
    -------
    None
        This function does not return anything.

    """
    while True:
        if os.path.exists(path):
            container.stop()
            container.remove()
            break


@app.route('/computation', methods=['POST'])
def handle_computation_request():
    """
    This function handles the computation request.
    It creates a new container and runs the image in it. It also calls async function which checks the container status and deletes the container once the container has exited
    It returns the container id.
    """
    print("inside handle_computation_request")
    # Get the JSON data from the request
    data = request.get_json()
    # Extract the necessary information from the data
    image = data['image']
    env_vars = data['env_vars']
    input_data = data['input_data']
    # Validate the data. If invalid, return an error response
    if not all([image, env_vars, input_data]):
        return jsonify({'error': 'Invalid request data'}), 400
    # If the data is valid, process the request
    # ...
    # Connect to the Docker daemon
    client = docker.from_env()
    path = os.path.join(os.getcwd(),input_data)
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    container = client.containers.run(
        image,
        detach=True,
        volumes={
            path: {'bind': '/data', 'mode': 'rw'}
        }
    )
    print(container.logs())
    # checkContainerStatus(container)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop.run_until_complete(testMountFile(container,path))
    loop.run_until_complete(checkContainerStatus(container))
    loop.close()
    # Return the container id
    return jsonify({'status': 'success', 'container_id': container.id})


@app.route('/containers', methods=['GET'])
def get_containers_status():
    """
        This function returns the status of all running containers.
        :return: A JSON object containing the status of all running containers.
    """
    # Connect to the Docker daemon
    client = docker.from_env()
    # Get a list of all running containers
    containers = client.containers.list(all=False)
    # Create a list to store the container status
    container_status = []
    # Iterate through the containers and get their status
    for container in containers:
        container_status.append({'id': container.id, 'status': container.status})
    # Return the container status
    return jsonify({'containers': container_status})


@app.route('/containers/<container_id>', methods=['DELETE'])
def stop_container(container_id):
    """
    This function Stop and remove a container.

    Parameters
    ----------
    container_id : str
        The ID of the container to stop and remove.

    Returns
    -------
    json
        A JSON response indicating whether the operation was successful.
    """
    # Connect to the Docker daemon
    client = docker.from_env()
    try:
        # Stop and remove the container
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        # Return a successful response
        return jsonify({'status': 'success'})
    except Exception as e:
        # Return an error response
        return jsonify({'error': str(e)}), 500


if (__name__ == '__main__'):
    app.run(debug=True)
