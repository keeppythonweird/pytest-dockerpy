# System testing with pytest and docker-py: example code!

This repo contains the example code which accompanies
the presentation
[System Testing with pytest and docker-py](https://docs.google.com/presentation/d/1w5WUw_LsnK5a79HzKyaEavu-po9MpSF33QTRPilKoX8).

<img align="right" src="cmdr_and_dockerpy.png">

The example code demonstrates how to use [pytest](http://pytest.org/latest/)
and [docker-py](https://github.com/docker/docker-py#docker-py).

In this repo:
* [test_screencast.py](./test_screencast.py) - Example tests, one that succceds,
                                               and one that fails.
* [conftest.py](./conftest.py) - pytest plugin to run our example service
* [service](./service) - An example HTTP service, to be run by the tests

In [conftest.py](./conftest.py), `pull_image` demonstrates how to pull an
image and check if it has succeeded, but is not used by the tests.

The test `test__error` isn't run by default, but if the `skip` is removed,
it will demonstrate docker logs being provided in the case of an error.

<img align="right" src="cmdr_and_pytest.png">

## Supported platforms

We have tested these examples successfully on:

* Linux

These platforms are not supported (the examples rely on being able to access
the IP of the running container from the host):

* docker-machine
* Docker beta for Mac or Windows

At this time (July 2016)
[the docker beta does not support accessing containers by IP from the host](https://forums.docker.com/t/host-excluded-from-bridge-network/12015).

### Running with docker-machine

If running with [docker-machine](https://docs.docker.com/machine/), the test
will rely on the environment variables set when you run
[docker-machine env](https://docs.docker.com/machine/reference/env/)
(`DOCKER_HOST`, `DOCKER_CERT_PATH`, `DOCKER_TLS_VERIFY`).

## Running tests

1. Build the example image:
  ```bash
  pushd service
  docker build -t service .
  popd
  ```
  
2. Install dependencies:

  ```bash
  (some_virtual_env) pip install -r test_requirements.txt
  ```
3. Run the tests:

  ```bash
  (some_virtual_env) py.test test_screencast.py
  ```

To demonstrate log output on test failure, remove `pytest.mark.skip` from
`test__error`.

## Thanks!

* Thanks to @BlueMonday for the code that checks if a pull request as failed,
  and for help with this problem in general!
* Thanks also to the test tools team
  (@BlueMonday, @MeabhG, Jordan Taekema) at @Demonware.

![](keep_python_weird.png)
