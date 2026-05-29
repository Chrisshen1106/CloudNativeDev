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

# To check code quality
## Install SonarCube
```shell
docker pull sonarqube
docker run --name sonarqube --restart always -p 9000:9000 -d sonarqube
```

## Run command
```shell
uv run pysonar \
  --sonar-host-url=http://localhost:9000 \
  --sonar-token=sqp_2b7359376a0829848870c2994d96ae73b1ccd416 \
  --sonar-python-coverage-report-paths=testing_report/coverage.xml \
  --sonar-python-xunit-report-path=testing_report/report.xml \
  --sonar-project-key=Cloud-Native
```

You will see the result on **sonar-host-url**