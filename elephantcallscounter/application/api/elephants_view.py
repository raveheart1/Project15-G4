import logging
from datetime import datetime

from flask import Blueprint, render_template, request

from elephantcallscounter import db
from elephantcallscounter.application.persistence.models.elephants import \
    Elephants
from elephantcallscounter.common.constants import LOCATION
from elephantcallscounter.config import env
from elephantcallscounter.utils.path_utils import get_project_root, join_paths

logger = logging.getLogger(__name__)

template_folder_loc = join_paths([get_project_root(), "app/templates"])

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

elephant_blueprint = Blueprint(
    "elephant", __name__, url_prefix="/elephants", template_folder=template_folder_loc
)


def _parse_datetime(field_name):
    """Parse a required datetime query parameter, raising ValueError on failure."""
    raw_value = request.args.get(field_name)
    if raw_value is None:
        raise ValueError("missing required parameter: %s" % field_name)
    try:
        return datetime.strptime(raw_value, TIME_FORMAT)
    except ValueError:
        raise ValueError(
            "invalid '%s'; expected format %s" % (field_name, TIME_FORMAT)
        )


@elephant_blueprint.route("/elephants_count/")
def elephant_counter():
    try:
        start_time = _parse_datetime("start_time")
        end_time = _parse_datetime("end_time")
    except ValueError as error:
        return {"error": str(error)}, 400
    elephants = db.session.query(Elephants).all()
    logger.info(start_time)
    logger.info(end_time)
    elephant_output = [
        {elephant.device_id: elephant.number_of_elephants} for elephant in elephants
    ]
    location_data = [
        LOCATION[elephant.device_id]
        for elephant in elephants
        if elephant.device_id in LOCATION
    ]
    return render_template(
        "index.html",
        number_of_elephants=elephant_output,
        locations_data=location_data,
        labels=list(LOCATION.keys()),
        google_api_key=env.GOOGLE_API_KEY,
    )


@elephant_blueprint.route("/add_elephant_count/")
def add_elephant_count():
    try:
        start_time = _parse_datetime("start_time")
        end_time = _parse_datetime("end_time")
        new_elephant = Elephants(
            latitude=float(request.args.get("latitude")),
            longitude=float(request.args.get("longitude")),
            start_time=start_time,
            end_time=end_time,
            device_id=request.args.get("device_id"),
            number_of_elephants=int(request.args.get("number_of_elephants")),
        )
    except (TypeError, ValueError) as error:
        return {"error": str(error)}, 400
    if new_elephant.device_id is None:
        return {"error": "missing required parameter: device_id"}, 400
    db.session.add(new_elephant)
    db.session.commit()

    return {"message": "new elephant added"}
