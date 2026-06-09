import json

import pytest

from elephantcallscounter.common import constants

pytestmark = pytest.mark.unit


def test_load_device_locations_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("DEVICE_LOCATIONS_FILE", raising=False)
    locations = constants.load_device_locations()
    assert set(locations) == {"nn01a", "nn01b", "nn02a", "nn01d"}
    # A copy is returned, not the module-level default.
    assert locations is not constants._DEFAULT_LOCATION


def test_load_device_locations_reads_override_file(tmp_path, monkeypatch):
    override = tmp_path / "device_locations.json"
    override.write_text(json.dumps({"zz99z": {"lat": 1.0, "lng": 2.0}}))
    monkeypatch.setenv("DEVICE_LOCATIONS_FILE", str(override))

    locations = constants.load_device_locations()
    assert locations == {"zz99z": {"lat": 1.0, "lng": 2.0}}


def test_load_device_locations_falls_back_on_bad_file(tmp_path, monkeypatch):
    bad = tmp_path / "broken.json"
    bad.write_text("{not valid json")
    monkeypatch.setenv("DEVICE_LOCATIONS_FILE", str(bad))

    locations = constants.load_device_locations()
    assert set(locations) == {"nn01a", "nn01b", "nn02a", "nn01d"}
