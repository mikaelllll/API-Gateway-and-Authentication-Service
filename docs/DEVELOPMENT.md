# Development

## Docker (recommended)

```bash
docker compose up --build
```

Open `http://localhost:8000`. Stop with `docker compose down`; add `-v` only when you intentionally want to delete local database and Redis volumes.

## Backend without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

SQLite is the development default. Start Redis locally for distributed rate limits; otherwise the development fallback is used.

## Frontend development

```bash
cd frontend
npm install
npm run dev
```

## Quality checks

```bash
ruff check app tests
pytest --cov=app
cd frontend && npm run build
docker compose build
```

CI repeats linting, backend tests, the production frontend build, and the final container build on pushes and pull requests.

