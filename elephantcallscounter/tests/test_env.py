import importlib

import pytest

pytestmark = pytest.mark.unit


def test_env_imports_without_optional_cloud_variables(monkeypatch):
    for variable_name in (
        "STORAGE_ACCOUNT_SAS_KEY",
        "CONNECTION_STRING",
        "AZURE_STORAGE_ACCOUNT",
        "IOT_HUB_CONN_STRING",
        "EVENTHUB_CONN_STRING",
        "GOOGLE_API_KEY",
    ):
        monkeypatch.delenv(variable_name, raising=False)

    from elephantcallscounter.config import env

    reloaded_env = importlib.reload(env)

    assert reloaded_env.STORAGE_SAS_KEY == ""
    assert reloaded_env.CONNECTION_STRING == ""
    assert reloaded_env.AZURE_STORAGE_ACCOUNT == ""
    assert reloaded_env.IOT_HUB_CONN_STRING == ""
    assert reloaded_env.EVENTHUB_CONN_STRING == ""
    assert reloaded_env.GOOGLE_API_KEY == ""
