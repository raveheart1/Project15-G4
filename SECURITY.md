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

## Dependency modernization (Flask 2/3 migration)

The application was originally pinned to a 2020-era Flask 1.x stack with known
CVEs in Flask 1.1.2, Werkzeug 1.0.1, and Jinja2 2.11.3 (debugger RCE,
multipart DoS, multiple XSS advisories). These could not be upgraded in
isolation because Flask 1.1.2 constrained `Werkzeug<2` / `Jinja2<3` and the app
depended on `flask-script` (removed in Flask 2+).

This has now been remediated by migrating to the modern stack:

- Flask `>=3.0`, Werkzeug `>=3.0`, Jinja2 `>=3.1.6`, Flask-SQLAlchemy `>=3.1`,
  Flask-Migrate `>=4.0`, SQLAlchemy `>=2.0`, click `>=8.1`.
- `flask-script` was removed entirely — the CLI commands already use Flask's
  native `flask <blueprint> <command>` interface, and Flask-Migrate registers
  the `flask db` group automatically.
- `flask-googlemaps` was dropped (it was unused; the map template uses the
  Google Maps JS API directly).
- Because Flask 3 requires Python >= 3.9, the frozen scientific pins
  (`pandas`, `scipy`, `numpy`, `librosa`, `opencv`, `tensorflow`) were
  modernized in lockstep and the Docker base image moved to `python:3.11-slim`.
  TensorFlow is held below 2.16 to keep Keras 2 (the model code still uses
  `ImageDataGenerator`).

Validation note: the Flask/app/CLI layer and the offline unit tests are
verified on the new stack. The audio/ML/cloud runtime paths (librosa,
TensorFlow, OpenCV, Azure/AWS) are not covered by the offline test suite and
were updated on a best-effort basis (e.g. the librosa `waveplot -> waveshow`
rename); they should be exercised against real data before production use.

To reproduce the dependency audit locally:

```bash
pip install pip-audit
pip-audit            # audits the currently installed environment
```

## Input handling

The public `/elephants` endpoints validate their query parameters and return
HTTP 400 on malformed input rather than surfacing unhandled 500s.
