# Sentinel API Gateway & Authentication Service

A production-style identity gateway built to demonstrate backend engineering, application security, distributed infrastructure, and a polished developer experience. The live security lab lets visitors exercise the real authentication lifecycle and inspect every API response.

## Run in GitHub Codespaces

1. Select **Code → Codespaces → Create codespace on main**.
2. If Codespaces asks, select **I trust the authors**.
3. Wait while PostgreSQL, Redis, the backend, and the frontend are built and started.
4. At the end of startup, the terminal prints the frontend URL under **OPEN THE FRONTEND**. Hold Ctrl (or Cmd on macOS) and select the link.

Codespaces does not open the application automatically. If startup completed before the visible terminal was ready and you cannot see the link, use either method below:

- Open the **Ports** tab, find port **8000** labelled **Sentinel Gateway**, then select its globe/open-browser icon.
- Run `bash .devcontainer/start.sh`. This checks the application and prints the frontend URL again without rebuilding it.

No local configuration is required. For local use, run `docker compose up --build` and open [http://localhost:8000](http://localhost:8000).

## What it demonstrates

- JWT access tokens with explicit expiration
- Rotating, server-stored refresh tokens and revocation
- OAuth2-compatible bearer authentication and interactive OpenAPI
- Role-based authorization (user, auditor, admin)
- Hashed API keys for service-to-service access
- Distributed Redis rate limiting
- Pydantic request validation and safe response models
- Argon2 password hashing
- Persistent security audit logs
- Async FastAPI, SQLAlchemy, PostgreSQL, React, TypeScript, Docker, CI

## Documentation

| Guide | Contents |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Components, request flow, data model, design decisions |
| [Security](docs/SECURITY.md) | Threat model and every implemented control |
| [API guide](docs/API.md) | Endpoints and example request flows |
| [Development](docs/DEVELOPMENT.md) | Local setup, testing, CI, project structure |

Interactive API documentation is available at `/api/docs` while the project is running.

## Important scope note

This is a portfolio reference implementation, not a drop-in identity provider. Production deployments should use managed secrets, TLS at the edge, database migrations, a dedicated OAuth provider, monitoring/alerting, and organization-specific security review.

## License

[MIT](LICENSE)

