from pathlib import Path

import pytest

from elephantcallscounter.data_processing.audio_processing import AudioProcessing
from elephantcallscounter.services.data_processing_service import create_file_segments

pytestmark = pytest.mark.unit

METADATA = """Selection\tHigh Freq (Hz)\tFile Offset (s)\tfilename\tduration\tmarginals
1\t36.6\t29314.08\tnn01d_20180127_000000.wav\t4.407\t
2\t31.2\t32552.884\tnn01d_20180127_000000.wav\t3.954\t
3\t39.1\t40181.978\tnn01d_20180127_000000.wav\t6.526\t
4\t42.4\t56860.315\tnn01b_20180220_000000.wav\t4.803\t
5\t40.6\t56895.621\tnn01b_20180220_000000.wav\t4.101\t
6\t43\t57212.231\tnn01b_20180220_000000.wav\t3.6207\t
7\t42.4\t57592.263\tnn01b_20180220_000000.wav\t6.6872\t
"""


def test_create_file_segments_uses_local_training_files(tmp_path, monkeypatch):
    metadata_file = tmp_path / "training_set.txt"
    metadata_file.write_text(METADATA)

    training_set = tmp_path / "TrainingSet"
    crop_set = tmp_path / "CroppedTrainingSet"
    (training_set / "nn01d").mkdir(parents=True)
    (training_set / "nn01b").mkdir(parents=True)
    (training_set / "nn01d" / "nn01d_20180127_000000.wav").write_bytes(b"wav")
    (training_set / "nn01b" / "nn01b_20180220_000000.wav").write_bytes(b"wav")

    def fake_crop_file(start_sec, end_sec, file_name, destination_file):
        Path(destination_file).parent.mkdir(parents=True, exist_ok=True)
        Path(destination_file).write_text(f"{start_sec}:{end_sec}:{file_name}")
        return 1

    monkeypatch.setattr(AudioProcessing, "crop_file", fake_crop_file)

    create_file_segments(
        str(metadata_file),
        training_set=str(training_set),
        crop_set=str(crop_set),
    )

    assert len(list((crop_set / "nn01d").iterdir())) == 3
    assert len(list((crop_set / "nn01b").iterdir())) == 4
    assert list((training_set / "nn01d").iterdir()) == []
    assert list((training_set / "nn01b").iterdir()) == []
