import pytest

from elephantcallscounter.services import pipeline_services
from elephantcallscounter.services.pipeline_services import pipeline_run

pytestmark = pytest.mark.unit


def test_run_pipeline_orchestrates_processing_without_publishing(monkeypatch):
    calls = {
        "analyse": [],
        "mono": [],
        "find": [],
        "run_cnn": [],
    }

    def fake_get_files_in_dir(path):
        if path == "data/demo/spectrogram":
            return ["spec_image_nn01d.png"]
        return ["nn01d_20180127_000000.wav"]

    def fake_analyse_sound_data(file_path, dest_path):
        calls["analyse"].append((file_path, dest_path))

    def fake_create_mono_spectrograms(image_folder, target_folder, write_file=False):
        calls["mono"].append((image_folder, target_folder, write_file))

    def fake_find_elephants_in_images(dir_name, dest_folder, csv_file_path):
        calls["find"].append((dir_name, dest_folder, csv_file_path))

    def fake_run_cnn(model_name, dir_path):
        calls["run_cnn"].append((model_name, dir_path))
        return [1]

    def fail_publish(*args, **kwargs):
        raise AssertionError("pipeline_run should not publish during this unit test")

    monkeypatch.setattr(pipeline_services, "get_files_in_dir", fake_get_files_in_dir)
    monkeypatch.setattr(
        pipeline_services, "analyse_sound_data", fake_analyse_sound_data
    )
    monkeypatch.setattr(
        pipeline_services, "create_mono_spectrograms", fake_create_mono_spectrograms
    )
    monkeypatch.setattr(
        pipeline_services, "find_elephants_in_images", fake_find_elephants_in_images
    )
    monkeypatch.setattr(pipeline_services, "run_cnn", fake_run_cnn)
    monkeypatch.setattr(pipeline_services.requests, "get", fail_publish)

    value = pipeline_run(
        "tests/test_fixtures",
        "data/demo/test_spec_image_labels.csv",
        publish_results=False,
    )

    assert value == [1]
    assert calls["analyse"][0][0] == "tests/test_fixtures/nn01d_20180127_000000.wav"
    assert calls["mono"][0][2] is True
    assert calls["find"][0][2].endswith("data/demo/test_spec_image_labels.csv")
    assert calls["run_cnn"] == [("binaries/resnet", "data/demo/spectrogram_bb")]
