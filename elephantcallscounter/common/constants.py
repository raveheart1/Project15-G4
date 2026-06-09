import json
import logging
import os

from elephantcallscounter.utils.path_utils import get_project_root

logger = logging.getLogger(__name__)

TRAINING_FILE_PATH_DEFAULT = os.path.join(
    get_project_root(), "data/metadata/nn_ele_hb_00-24hr_TrainingSet_v2.txt"
)
TEST_PATH_DEFAULT = os.path.join(
    get_project_root(), "data/metadata/nn_ele_00-24hr_GeneralTest_v4.txt"
)
RUN_FRESH = True

# Approximate, intentionally coarse region centroids for the acoustic
# monitoring sites. Precise sensor coordinates for a poaching-vulnerable
# species should NOT be committed to a public repository -- see DATA_ETHICS.md.
# Override these at runtime (without committing real coordinates) by pointing
# the DEVICE_LOCATIONS_FILE environment variable at a JSON file of the same
# shape: {"nn01a": {"lat": ..., "lng": ...}, ...}.
_DEFAULT_LOCATION = {
    "nn01a": {"lat": 2.5, "lng": 16.4},
    "nn01b": {"lat": 2.9, "lng": 16.3},
    "nn02a": {"lat": 2.2, "lng": 16.7},
    "nn01d": {"lat": 3.5, "lng": 17.8},
}


def load_device_locations():
    """Load device coordinates, preferring an out-of-repo override file.

    Reads ``os.environ`` directly (rather than the config.env module) to avoid
    a circular import, since config.env imports this module.

    :return dict: ``{device_id: {"lat": float, "lng": float}}``
    """
    path = os.environ.get("DEVICE_LOCATIONS_FILE")
    if path:
        try:
            with open(path) as handle:
                return json.load(handle)
        except (OSError, ValueError) as error:
            logger.warning(
                "Could not load DEVICE_LOCATIONS_FILE=%s (%s); "
                "falling back to approximate defaults.",
                path,
                error,
            )
    return dict(_DEFAULT_LOCATION)


LOCATION = load_device_locations()
