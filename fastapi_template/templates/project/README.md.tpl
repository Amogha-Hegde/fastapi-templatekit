# $project_name

```bash
uv sync
uv run uvicorn $package_name.main:app --reload
```

List registered HTTP and websocket routes:

```bash
uv run $package_name urls
```
