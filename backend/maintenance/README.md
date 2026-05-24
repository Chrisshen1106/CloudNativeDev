# Setup environment

## Install `uv`
```shell
# For linux and MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
# For windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## setup environment
```shell
uv sync
```

## setup environment variable
```shell
cp .env.example .env
```

Modify the `.env`


# To run this service

## Development mode
```shell
uv run -m flask --app app run --port 8000
```

## Production mode
```shell
uv run gunicorn "app:app" --bind 0.0.0.0:8000
```

# To test this service

Run the following command under the `/backend/maintenance/` folder.

```shell
mkdir -p testing_report && \
uv run -m pytest -v -rA \
  --html=testing_report/report.html \
  --self-contained-html \
  --junitxml=testing_report/report.xml \
  --cov=. \
  --cov-report=term-missing \
  --cov-report=html:testing_report/htmlcov \
  --cov-report=xml:testing_report/coverage.xml
```

It will output reports under the `testing_report` folder.

```
testing_report/
├── report.html ----> testing report
├── report.xml  ----> testing report for CI
├── coverage.xml ---> Code coverage summary for CI
└── htmlcov/ -------> Code coverage summary
    └── index.html
```