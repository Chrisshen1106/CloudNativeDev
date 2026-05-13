# Asset Service

資產管理微服務，負責資產的查詢、新增、編輯與刪除。

# Setup environment

## Install `uv`
```shell
# For Linux and MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
# For Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setup dependencies
```shell
uv sync
```

## Setup environment variable
```shell
cp .env.example .env
```

Modify the `.env` file and fill in the following:
```
SQLALCHEMY_DATABASE_URI=mysql+pymysql://<user>:<password>@<host>:<port>/<database>
JWT_SECRET_KEY=<shared secret key>
```

# To run this service

## Development mode
```shell
# Windows (PowerShell)
$env:PYTHONUTF8=1; uv run -m flask --app app run --port 8000

# Linux / MacOS / Git Bash
PYTHONUTF8=1 uv run -m flask --app app run --port 8000
```

## Production mode
```shell
uv run gunicorn "app:app" --bind 0.0.0.0:8000
```

# API

| Method | Path | 權限 | 說明 |
|--------|------|------|------|
| GET | `/api/user` | user / admin | 取得資產列表（user 只看自己的，admin 看全部） |
| GET | `/api/assets/<id>` | user / admin | 取得單一資產詳情（含維修紀錄） |
| POST | `/api/assets` | admin | 新增資產 |
| PUT | `/api/assets/<id>` | admin | 編輯資產 |
| DELETE | `/api/assets/<id>` | admin | 刪除資產 |

所有 API 需在 Header 帶 JWT Token：
```
Authorization: Bearer <token>
```

# Error Codes

| Status Code | 說明 | Response 範例 |
|-------------|------|---------------|
| `400` | 未提供資料或格式錯誤 | `{"message": "未提供資料"}` |
| `401` | 未帶 JWT Token | `{"msg": "Missing Authorization Header"}` |
| `403` | 權限不足（user 存取他人資產，或 user 嘗試新增/編輯/刪除） | `{"message": "權限不足"}` |
| `404` | 找不到指定資產 | `{"message": "找不到資源"}` |
| `500` | 伺服器內部錯誤 | `{"message": "新增資產失敗", "error": "..."}` |

# Generate test token (for development only)
```shell
uv run python gen_token.py
```
