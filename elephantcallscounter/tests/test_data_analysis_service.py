import sys
from types import ModuleType

import pytest

from elephantcallscounter.services.data_analysis_service import run_cnn

pytestmark = pytest.mark.unit


def test_run_cnn_passes_model_name_to_resnet_without_loading_tensorflow(monkeypatch):
    calls = {}

    class FakeElephantCounterResnet:
        def __init__(self, model_name):
            calls["model_name"] = model_name

        def run_model(self, dir_path):
            calls["dir_path"] = dir_path
            return [1, 0]

    fake_resnet_module = ModuleType("elephantcallscounter.models.resnet_model")
    fake_resnet_module.ElephantCounterResnet = FakeElephantCounterResnet
    monkeypatch.setitem(
        sys.modules,
        "elephantcallscounter.models.resnet_model",
        fake_resnet_module,
    )

    result = run_cnn("binaries/resnet", "data/demo/spectrogram_bb")

    assert result == [1, 0]
    assert calls == {
        "model_name": "binaries/resnet_",
        "dir_path": "data/demo/spectrogram_bb",
    }
