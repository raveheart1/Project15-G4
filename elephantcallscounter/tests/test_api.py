import pytest

from elephantcallscounter import db
from elephantcallscounter.app_factory import create_app
from elephantcallscounter.application.persistence.models.elephants import Elephants

pytestmark = pytest.mark.unit


def test_add_elephants_count():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        },
        register_cli=False,
        register_blob_events=False,
    )

    with app.app_context():
        db.create_all()
        try:
            response = app.test_client().get(
                "/elephants/add_elephant_count/",
                query_string={
                    "latitude": "20",
                    "longitude": "30",
                    "start_time": "2020-01-10 06:30:23",
                    "end_time": "2021-01-11 06:30:23",
                    "device_id": "1",
                    "number_of_elephants": "1",
                },
            )

            assert response.status_code == 200
            assert response.get_json() == {"message": "new elephant added"}

            elephant = Elephants.query.one()
            assert elephant.latitude == 20
            assert elephant.longitude == 30
            assert elephant.device_id == "1"
            assert elephant.number_of_elephants == 1
        finally:
            db.session.remove()
            db.drop_all()
