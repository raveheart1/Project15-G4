# Data ethics & sensitivity

This project processes acoustic data from a wild population of **forest
elephants** (a poaching-vulnerable, IUCN Critically Endangered species) at
monitoring sites associated with the Elephant Listening Project. Some of the
data handled here is sensitive and should be treated with care, especially in a
**public** repository.

## Location data

`elephantcallscounter/common/constants.py` maps device ids to latitude /
longitude, and the web UI renders these on a map. Publishing the precise
locations of acoustic sensors — or of detected animals — is a recognised risk
in conservation technology, because it can aid poachers.

Guidance:

- The coordinates committed in this repository are **approximate region
  centroids**, not exact sensor positions, and are intended only to make the
  demo map render.
- Do **not** commit precise sensor or detection coordinates. Supply real
  coordinates at runtime via a file that is kept out of version control:

  ```bash
  export DEVICE_LOCATIONS_FILE=/secure/path/device_locations.json
  ```

  where the JSON has the shape
  `{"nn01a": {"lat": ..., "lng": ...}, ...}`.
- Maintainers with domain knowledge should decide what spatial precision (if
  any) is appropriate to publish, and consider coarsening or removing even the
  approximate values above.

## Recorded audio and detections

- Raw `.wav` recordings and trained model artifacts are intentionally **not**
  committed (see `.gitignore` and `elephantcallscounter/binaries/README.md`).
- Detection outputs that pair a count with a precise time and location are
  themselves sensitive; aggregate or coarsen before sharing publicly.

## Secrets

- A Google Maps API key was previously committed in the map template. It has
  been moved to the `GOOGLE_API_KEY` environment variable, but it **remains in
  the git history and must be rotated** by someone with access to the Google
  Cloud project. See `SECURITY.md`.
- Cloud/storage credentials must only be provided via environment variables /
  `.env` (git-ignored), never committed.

## Attribution & licensing

The data originates from Cornell University's Elephant Listening Project and
Microsoft Project 15. Respect the terms under which it was shared, and consult
the project owners before redistributing data or derived artifacts.
