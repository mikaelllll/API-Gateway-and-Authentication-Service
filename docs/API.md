# API guide

The canonical, executable contract is available at `/api/docs`.

| Method | Path | Purpose | Authentication |
|---|---|---|---|
| GET | `/api/health` | Readiness signal | Public |
| POST | `/api/auth/register` | Create an identity | Public |
| POST | `/api/auth/login` | Issue access/refresh pair | Public |
| POST | `/api/oauth/token` | OAuth2 form token endpoint | Public |
| POST | `/api/auth/refresh` | Rotate token pair | Refresh token |
| POST | `/api/auth/revoke` | Revoke refresh token | Refresh token |
| GET | `/api/me` | Resolve current identity | Bearer JWT |
| GET | `/api/admin/overview` | Demonstrate admin RBAC | Admin JWT |
| POST | `/api/api-keys` | Create a machine key | Bearer JWT |
| GET | `/api/service/data` | Machine-protected resource | `X-API-Key` |
| GET | `/api/audit` | Read permitted audit events | Bearer JWT |
| POST | `/api/lab/password-hash` | Demonstrate Argon2 hash and verification | Public demo endpoint |
| GET | `/api/lab/rate-limit` | Dedicated target for the HTTP 429 demonstration | Public demo endpoint |

The frontend's Security Lab runs these calls in sequence and displays status, latency, and JSON feedback.
