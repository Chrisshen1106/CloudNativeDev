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

# To run this server

```shell
uv run -m flask --app app run
```