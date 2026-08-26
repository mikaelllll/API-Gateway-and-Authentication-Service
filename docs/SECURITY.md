# Security design

## Controls

- Passwords use Argon2 through `pwdlib`; plaintext is never stored or returned.
- JWT access tokens are signed, typed, uniquely identified, and expire after 15 minutes by default.
- Refresh tokens are opaque random values. Only SHA-256 digests are stored. Every refresh rotates and invalidates the previous token.
- Logout/revocation is idempotent and invalidates server-side refresh state.
- API keys are shown once, stored only as digests, and carry an identifiable prefix.
- RBAC is enforced as a dependency at the protected route—not hidden in UI logic.
- Rate limiting uses Redis so the policy is shared by replicas; a local fallback supports offline development.
- Validation rejects malformed emails, weak passwords, oversized values, and invalid types.
- Audit logs record actor, action, outcome, time, source address, and safe details.
- Browser responses include clickjacking, MIME sniffing, and referrer protections.

## OAuth2

The project exposes an OAuth2 password-flow token endpoint for its first-party interactive API documentation. Social/provider authorization requires real client credentials and callback URLs, so it is deliberately an integration boundary rather than a fake provider flow. In production, replace the password flow with Authorization Code + PKCE through an OIDC provider such as Keycloak, Auth0, Cognito, or an organization IdP, validating issuer, audience, signature, nonce, and state.

## Production hardening

Use a secret manager, asymmetric key rotation, TLS, CSRF protection if cookies are introduced, Alembic migrations, centralized immutable audit storage, alerting, backups, dependency scanning, and an external penetration test.
