import pprint
import os

import docker
import docker.tls
import pytest

import labels


IMAGE = "service"
DOCKER_HOST = os.environ.get('DOCKER_HOST', 'unix://var/run/docker.sock')
DOCKER_CERT_PATH = os.environ.get('DOCKER_CERT_PATH')
DOCKER_TLS_VERIFY = os.environ.get('DOCKER_TLS_VERIFY', '0') == '1'



def _docker_client():
    if DOCKER_HOST.startswith('unix'):
        return docker.Client(DOCKER_HOST, version='auto')
    else:
        tls_config = docker.tls.TLSConfig(
            client_cert=(
                os.path.join(DOCKER_CERT_PATH, 'cert.pem'),
                os.path.join(DOCKER_CERT_PATH, 'key.pem')),
            ca_cert=os.path.join(DOCKER_CERT_PATH, 'ca.pem'),
            verify=DOCKER_TLS_VERIFY,
        )
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


@pytest.yield_fixture
def example_container():
    docker_client = _docker_client()

    docker_client.pull(IMAGE)
    container = docker_client.create_container(
        image=IMAGE,
        detach=True,
        labels=[labels.CONTAINERS_FOR_TESTING_LABEL],
        environment={'VIRTUAL_HOST': 'example.docker'},
    )
    docker_client.start(container=container["Id"])
    container_info = docker_client.inspect_container(container.get('Id'))

    if DOCKER_HOST.startswith('unix'):
        yield container_info["NetworkSettings"]["IPAddress"]
    else:
        yield 'example.docker'

    if docker_client.inspect_container(container=container["Id"])["State"]["Running"]:
        docker_client.kill(container=container["Id"])
    docker_client.remove_container(
        container=container["Id"],
        force=True
    )
