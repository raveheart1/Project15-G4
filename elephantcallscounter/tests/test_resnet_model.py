import pytest

from elephantcallscounter.models.resnet_model import ElephantCounterResnet

pytestmark = pytest.mark.unit


class FakeModel:
    def predict(self, data_it):
        return [
            [0.1, 0.8, 0.1],
            [0.7, 0.2, 0.1],
            [0.2, 0.3, 0.5],
        ]


def test_predict_classes_uses_predict_argmax_for_keras_compatibility():
    assert ElephantCounterResnet.predict_classes(FakeModel(), object()).tolist() == [
        1,
        0,
        2,
    ]


def test_run_model_loads_saved_model_from_relative_model_path(monkeypatch):
    counter = ElephantCounterResnet.__new__(ElephantCounterResnet)
    counter.model_save_loc = "binaries/resnet_25_epoch"
    calls = {}

    def fake_get_dataset_it(dir_path):
        calls["dataset_dir_path"] = dir_path
        return "dataset"

    def fake_load_model(model_save_loc):
        calls["model_save_loc"] = model_save_loc
        return FakeModel()

    monkeypatch.setattr(counter, "get_dataset_it", fake_get_dataset_it)
    monkeypatch.setattr(counter, "load_model", fake_load_model)

    result = counter.run_model("data/demo/spectrogram_bb")

    assert result.tolist() == [1, 0, 2]
    assert calls["dataset_dir_path"].endswith("data/demo/spectrogram_bb")
    assert calls["model_save_loc"] == "binaries/resnet_25_epoch"
