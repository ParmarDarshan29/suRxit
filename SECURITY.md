# Security Policy


## PHI Handling
- All Protected Health Information (PHI) must be encrypted in transit and at rest.
- Never log or expose PHI in plaintext.



## HTTPS/TLS
- All external and internal service communication must use HTTPS/TLS 1.2+.


## Encrypted Storage
- Use industry-standard encryption (AES-256) for all sensitive data.
- Keys must be managed via a secure vault (e.g., HashiCorp Vault).


## RBAC
- Enforce Role-Based Access Control for all user and service actions.
- Principle of least privilege applies to all roles.

