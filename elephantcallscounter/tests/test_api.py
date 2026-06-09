import pytest

from elephantcallscounter import db
from elephantcallscounter.app_factory import create_app
from elephantcallscounter.application.persistence.models.elephants import Elephants

pytestmark = pytest.mark.unit


def _make_app():
    return create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        },
        register_cli=False,
        register_blob_events=False,
    )


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


def test_add_elephant_count_rejects_bad_timestamp():
    app = _make_app()
    with app.app_context():
        db.create_all()
        try:
            response = app.test_client().get(
                "/elephants/add_elephant_count/",
                query_string={
                    "latitude": "20",
                    "longitude": "30",
                    "start_time": "not-a-date",
                    "end_time": "2021-01-11 06:30:23",
                    "device_id": "1",
                    "number_of_elephants": "1",
                },
            )

            assert response.status_code == 400
            assert "start_time" in response.get_json()["error"]
            assert Elephants.query.count() == 0
        finally:
            db.session.remove()
            db.drop_all()


def test_add_elephant_count_rejects_missing_device_id():
    app = _make_app()
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
                    "number_of_elephants": "1",
                },
            )

            assert response.status_code == 400
            assert Elephants.query.count() == 0
        finally:
            db.session.remove()
            db.drop_all()


def test_elephants_count_renders_api_key_from_env(monkeypatch):
    from elephantcallscounter.config import env

    monkeypatch.setattr(env, "GOOGLE_API_KEY", "test-key-123")
    app = _make_app()
    with app.app_context():
        db.create_all()
        try:
            response = app.test_client().get(
                "/elephants/elephants_count/",
                query_string={
                    "start_time": "2020-01-10 06:30:23",
                    "end_time": "2021-01-11 06:30:23",
                },
            )

            assert response.status_code == 200
            assert b"test-key-123" in response.data
            assert b"AIzaSyBdxfwE2tv" not in response.data
        finally:
            db.session.remove()
            db.drop_all()
