import json
import pprint
import os
import shlex
import subprocess

import docker
import pytest

import labels


IMAGE = "service"


def _docker_client():
    return docker.Client('unix://var/run/docker.sock', version="auto")


def pytest_runtest_logreport(report):
    """ If the test has failed, include docker logs in the report

    Any containers which have been labelled with
    `labels.CONTAINERS_FOR_TESTING_LABEL` will have their logs dumped int
    a section of the pytest report, so that users can use this information
    to debug the test failure.

    :param report: An object provided by `pytest` which provides information
                   about the status of the test.
    """
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
            report.longrepr.addsection(
                'docker logs',
                # If this output is in bytes, python3 will not allow us
                # to join it
                os.linesep.join([str(l) for l in log_lines]))


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


def example_container_with_docker_py():
    docker_client = _docker_client()

    container = docker_client.create_container(
        image=IMAGE,
        labels=[labels.CONTAINERS_FOR_TESTING_LABEL]
    )
    docker_client.start(container=container["Id"])
    container_info = docker_client.inspect_container(container.get('Id'))

    yield container_info["NetworkSettings"]["IPAddress"]

    docker_client.remove_container(
        container=container["Id"],
        force=True
    )


def example_container_with_docker_compose():
    subprocess.check_output(shlex.split("docker-compose up -d"))

    docker_client = _docker_client()
    container_info = docker_client.inspect_container("examplecontainer")
    # Get the IP address using the network docker-compose automatically creates
    yield container_info["NetworkSettings"]["Networks"]["pytestdockerpy_default"]["IPAddress"]

    subprocess.check_output(shlex.split("docker-compose down"))


@pytest.yield_fixture(params=[
    "use_docker_py",
    "use_docker_compose"])
def example_container(request):
    if request.param == "use_docker_py":
        yield next(example_container_with_docker_py())
    elif request.param == "use_docker_compose":
        yield next(example_container_with_docker_compose())
