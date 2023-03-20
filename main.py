import threading
import os
import docker
import json
import time
from docker.errors import ImageNotFound, APIError
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

swagger_url = '/swagger'
api_url = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    swagger_url,
    api_url,
    config={
        'app_name': "SwitchBoardSimulator"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)


def remove_container_on_exit(container):
    """
    This function checks the container status and deletes the container once it has exited.
    """
    try:
        while True:
            container.reload()
            container_state = container.attrs["State"]
            print(container_state)

            if (container_state["Status"] == "exited"):
                container.remove()
                break

            time.sleep(10)

    except Exception as e:
        print(f'Error checking container status: {e}')


@app.route('/computation', methods=['POST'])
def handle_computation_request():
    """
    This function handles the computation request.
    It creates a container and runs the image in it.
    It also starts a thread to remove the container when the computation is done.
    :return: A JSON response containing the status and container id.
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return {'error': 'Invalid JSON data in the request.'}, 400
        # Extract the necessary information from the data
        image = data.get('image')
        env_vars = data.get('env_vars')
        input_data = data.get('input_data')
        # Validate the data. If invalid, return an error response
        if not all([image, env_vars, input_data]):
            return {'error': 'Invalid request data.'}, 400
        path_on_host = os.path.join(os.getcwd(), input_data['resultFolder'])
        path_on_container = input_data['containerVolumePath']

        # Check if input data exists
        if not os.path.exists(path_on_host):
            os.makedirs(path_on_host)

        # Connect to the Docker daemon
        client = docker.from_env()

        # Check if the image exists
        try:
            # client.images.get(image)
            client.images.pull(image)
        except docker.errors.APIError:
            return {'error': f'Image "{image}" not found.'}, 404

        # Create a container and run the image in it
        container = client.containers.run(
            image,
            detach=True,
            environment=env_vars,
            volumes={
                path_on_host: {'bind': path_on_container, 'mode': 'rw'}
            }
        )
        # create a variable to get the timestamp when container was started, This is the stop condition for Approach-2
        timestamp = time.time()

        # Stop and remove container when job is done

        # Approach-1 : By using exit code
        # call remove_container_on_exit with container name
        # This function checks if container has finished is by using the exit code of the container.
        # threading.Thread(target=remove_container_on_exit, args=(container,)).start()

        # Approach-2 : By checking file writes in storage location
        # call remove_container_on_completion
        # This function checks when computation writes a specific file in the directory then assume the computation is finished and stop & remove the container.
        threading.Thread(target=remove_container_on_completion, args=(container, path_on_host, timestamp)).start()

        # Return the container id
        return {'status': 'success', 'container_id': container.id}, 200
    except BadRequest as e:
        return {'error': f'Request JSON body decoding error: {e}.'}, 500
    except APIError as e:
        return {'error': f'Docker API error: {e}.'}, 500
    except Exception as e:
        return {'error': f'Unknown error: {e}.'}, 500


def remove_container_on_completion(container, folder_path, timestamp):
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
    try:
        while True:
            container.reload()
            container_state = container.attrs["State"]
            print(container_state)
            if (container_state["Status"] == "exited"):
                container.remove()
                break
            # check if any file {result_timestamp} in folder path is created after the timestamp
            # if not, wait for 1 second and check again
            if not any(os.path.getmtime(os.path.join(folder_path, f)) > timestamp for f in os.listdir(folder_path)):
                print("Waiting for file to be created...")
                time.sleep(5)
            else:
                print("File created!")
                container.stop()
                container.remove()
                print("Container stopped!")
                break
    except Exception as e:
        print("exception", e)
        # Raise an exception in case of an error
        raise Exception(str(e))


@app.route('/containers', methods=['GET'])
def get_containers_status():
    """
        This function returns the status of all running containers.
        :return: A JSON object containing the status of all running containers.
    """
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)})


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
    try:
        # Connect to the Docker daemon
        client = docker.from_env()
        # Get the container by ID
        container = client.containers.get(container_id)
        # Stop and remove the container
        container.stop()
        container.remove()
        # Return a successful response
        return jsonify({'status': 'success'})
    except docker.errors.NotFound:
        # Return a 404 error response if container is not found
        return jsonify({'error': f'Container with ID {container_id} not found'}), 404
    except docker.errors.APIError as e:
        # Return a 500 error response if an API error occurs
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def check_health():
    """
    This function is used to check the health of the application.
    :return: A string message indicating the health of the application.
    """
    return "Health Check OK : Application is running"


if (__name__ == '__main__'):
    app.run(debug=True)
