# Security notes

## Reporting

This is an academic research project (Oxford AI: Cloud and Edge
Implementations, 2020-21). For security concerns, reach out to one of the
developers listed in the README.

## Secrets

- Do **not** commit credentials. Copy `.env.example` to `.env` and populate it
  locally; `.env` is git-ignored.
- The Google Maps API key is now read from the `GOOGLE_API_KEY` environment
  variable and injected into the template at render time. A key was previously
  committed in `application/templates/index.html`; it remains in git history
  and **must be treated as compromised and rotated** in the Google Cloud
  console.

## Known vulnerable dependencies

The application is pinned to a 2020-era Flask 1.x stack. `pip-audit` reports
known CVEs in these pinned packages, which cannot be upgraded in isolation:

| Package  | Pinned   | Notable advisories                                   | Fixed in        |
|----------|----------|------------------------------------------------------|-----------------|
| Flask    | 1.1.2    | PYSEC-2023-62, CVE-2026-27205                         | 2.2.5 / 3.1.3   |
| Werkzeug | 1.0.1    | debugger RCE, multipart DoS (multiple PYSEC/CVE)      | 2.x / 3.x       |
| Jinja2   | 2.11.3   | CVE-2024-22195, -34064, -56326, CVE-2025-27516 (XSS)  | 3.1.6           |

Flask 1.1.2 constrains `Werkzeug<2` and `Jinja2<3`, and the project depends on
`flask-script` (removed in Flask 2+). Remediation therefore requires a
coordinated **Flask 2/3 migration** (replacing `flask-script` with the native
Flask CLI), which is a tracked follow-up rather than a drop-in version bump.

To reproduce the audit locally:

```bash
pip install pip-audit
pip-audit            # audits the currently installed environment
```

## Input handling

The public `/elephants` endpoints validate their query parameters and return
HTTP 400 on malformed input rather than surfacing unhandled 500s.
