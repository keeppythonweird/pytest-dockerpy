import backoff
import pytest
import requests


@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError),
                      max_tries=2)
def _get_request(example_container):
    return requests.get("http://{url}/".format(url=example_container))


def test__works(example_container):
    result = _get_request(example_container)
    assert result.json() == {"status": "alive"}


@pytest.mark.skip(reason="For demonstrating log output on failure")
def test__error(example_container):
    raise Exception("oh no!")
