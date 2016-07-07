# System testing with pytest and docker-py: example code!

This code demonstrates how to use [pytest](http://pytest.org/latest/) and
[docker-py](https://github.com/docker/docker-py#docker-py).

In this repo:
* [test_screencast.py](./test_screencast.py) - Example tests, one that succceds,
                                               and one that fails.
* [conftest.py](./conftest.py) - pytest plugin to run our example service
* [service](./service) - An example HTTP service, to be run by the tests

## Building

```bash
pushd service
docker build -t service .
popd
```

## Running tests

```bash
pip install pytest docker-py backoff
py.test test_screencast.py
```

To demonstrate log output on test failure, remove `pytest.mark.skip` from
`test__error`.

## Running with docker-machine

If running with [docker-machine](https://docs.docker.com/machine/), the test
will rely on these environment variables:

* Set `DOCKER_CERT_PATH` to specify where our docker certs are located, if 
  you are using them
* Set `DOCKER_TLS_VERIFY` to 1 if you would like TLS verification
* `DOCKER_HOST` is set for you by docker-machine and specifies how to connect
  to the docker daemon, e.g. docker socket or other
  
## Example code

In [conftest.py](./conftest.py), `pull_image` demonstrates how to pull an
image and check if it has succeeded, but is not used by the tests.

The test `test__error` isn't run by default, but if the `skip` is removed,
it will demonstrate docker logs being provided in the case of an error.
