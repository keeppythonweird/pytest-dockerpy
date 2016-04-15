import pytest

@pytest.yield_fixture
def foo():
    print "foo"
    yield "bar"
    print "baz"

def test(foo):
    print foo