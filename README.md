# Example code to accompany presentation

## Building

```bash
docker build -t service .
```

## Running tests

```bash
pip install pytest docker-py backoff
pytest test_screencast.py
```

To demonstrate log output on test failure, remove `pytest.mark.skip` from
`test__error`.
