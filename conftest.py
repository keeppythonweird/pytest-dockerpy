import json
import pprint
import os

import docker
import docker.tls
import pytest

import labels


IMAGE = "service"

# Support for docker-machine, environment variables set by
# docker-machine env (https://docs.docker.com/machine/reference/env/)
DOCKER_HOST = os.environ.get('DOCKER_HOST', 'unix://var/run/docker.sock')
DOCKER_CERT_PATH = os.environ.get('DOCKER_CERT_PATH')
DOCKER_TLS_VERIFY = os.environ.get('DOCKER_TLS_VERIFY', '0') == '1'
DOCKER_MACHINE_HOSTNAME = "example.docker"
USING_DOCKER_MACHINE = True if not DOCKER_HOST.startswith("unix") else False


def _docker_client():
    if USING_DOCKER_MACHINE:
        tls_config = docker.tls.TLSConfig(
            client_cert=(
                os.path.join(DOCKER_CERT_PATH, 'cert.pem'),
                os.path.join(DOCKER_CERT_PATH, 'key.pem')),
            ca_cert=os.path.join(DOCKER_CERT_PATH, 'ca.pem'),
            verify=DOCKER_TLS_VERIFY,
        )
    else:
        tls_config = False
    return docker.Client(DOCKER_HOST, version="auto", tls=tls_config)


def pytest_runtest_logreport(report):
    if report.failed:
        docker_client = _docker_client()
        test_containers = docker_client.containers(
            all=True,
            filters={"label": labels.CONTAINERS_FOR_TESTING_LABEL})
        for container in test_containers:
            log_lines = [
                ("docker inspect {!r}:".format(container['Id'])),
                (pprint.pformat(docker_client.inspect_container(container['Id']))),
                ("docker logs {!r}:".format(container['Id'])),
                (docker_client.logs(container['Id'])),
            ]
            report.longrepr.addsection('docker logs', os.linesep.join(log_lines))


def pull_image(image):
    """ Pull the specified image using docker-py

    This function will parse the result from docker-py and raise an exception
    if there is an error.

    :param image: Name of the image to pull
    """
    docker_client = _docker_client()
    response = docker_client.pull(image)
    lines = [line for line in response.splitlines() if line]

    # The last line of the response contains the overall result of the pull
    # operation.
    pull_result = json.loads(lines[-1])
    if "error" in pull_result:
        raise Exception("Could not pull {}: {}".format(
            image, pull_result["error"]))


@pytest.yield_fixture
def example_container():
    docker_client = _docker_client()
    environment_vars = {'VIRTUAL_HOST': DOCKER_MACHINE_HOSTNAME} if USING_DOCKER_MACHINE else None

    container = docker_client.create_container(
        image=IMAGE,
        labels=[labels.CONTAINERS_FOR_TESTING_LABEL],
        environment=environment_vars
    )
    docker_client.start(container=container["Id"])
    container_info = docker_client.inspect_container(container.get('Id'))

    if USING_DOCKER_MACHINE:
        yield DOCKER_MACHINE_HOSTNAME
    else:
        yield container_info["NetworkSettings"]["IPAddress"]

    docker_client.remove_container(
        container=container["Id"],
        force=True
    )
