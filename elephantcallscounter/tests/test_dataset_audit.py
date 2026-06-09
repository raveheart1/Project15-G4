import pytest

from elephantcallscounter.evaluation import dataset_audit

pytestmark = pytest.mark.unit


def _make_boxed_dir(tmp_path, layout):
    """Create a fake spectrogram_bb dir: {count_label: [file_names]}."""
    boxed = tmp_path / "spectrogram_bb"
    for label, names in layout.items():
        folder = boxed / str(label)
        folder.mkdir(parents=True)
        for name in names:
            (folder / name).write_bytes(b"")
    return str(boxed)


def test_summarize_counts_images_per_class(tmp_path):
    boxed = _make_boxed_dir(
        tmp_path,
        {0: ["a.png"], 1: ["b.png", "c.png"], 2: ["d.png"]},
    )
    assert dataset_audit.summarize_boxed_dataset(boxed) == {0: 1, 1: 2, 2: 1}


def test_iter_boxed_labels_ignores_non_count_folders_and_non_images(tmp_path):
    boxed = _make_boxed_dir(tmp_path, {1: ["keep.png", "skip.txt"]})
    (tmp_path / "spectrogram_bb" / "notes").mkdir()  # non-count folder
    rows = list(dataset_audit.iter_boxed_labels(boxed))
    assert rows == [("keep.png", 1)]


def test_rebuild_then_audit_round_trips(tmp_path):
    boxed = _make_boxed_dir(tmp_path, {0: ["z.png"], 2: ["x.png", "y.png"]})
    csv_path = str(tmp_path / "labels" / "labels.csv")

    written = dataset_audit.write_labels_csv(
        dataset_audit.build_labels(boxed), csv_path
    )
    assert written == 3

    report = dataset_audit.audit_labels_csv(csv_path, boxed)
    assert report["valid"] is True
    assert report["malformed_rows"] == 0
    assert report["expected_total"] == report["found_total"] == 3


def test_audit_flags_corrupt_csv(tmp_path):
    boxed = _make_boxed_dir(tmp_path, {1: ["a.png"]})
    csv_path = tmp_path / "labels.csv"
    # A header that does not match the expected columns -> every row malformed.
    csv_path.write_text(",file_name,number_of_elephants\n0,0,garbage\n")

    report = dataset_audit.audit_labels_csv(str(csv_path), boxed)
    assert report["valid"] is False
    assert report["malformed_rows"] == 1
    assert report["missing"] == ["a.png"]


def test_audit_detects_count_mismatch(tmp_path):
    boxed = _make_boxed_dir(tmp_path, {2: ["a.png"]})
    csv_path = tmp_path / "labels.csv"
    csv_path.write_text("file_name,number_of_elephants\na.png,1\n")

    report = dataset_audit.audit_labels_csv(str(csv_path), boxed)
    assert report["mismatched"] == ["a.png"]
    assert report["valid"] is False


def test_score_predictions_computes_accuracy_and_confusion():
    predictions = {"a": 1, "b": 2, "c": 0}
    ground_truth = {"a": 1, "b": 1, "c": 0}  # b is wrong
    result = dataset_audit.score_predictions(predictions, ground_truth)
    assert result["n"] == 3
    assert result["accuracy"] == pytest.approx(2 / 3)
    assert result["confusion"][(1, 2)] == 1  # true 1, predicted 2


def test_score_predictions_handles_no_overlap():
    result = dataset_audit.score_predictions({"a": 1}, {"b": 1})
    assert result == {"accuracy": None, "n": 0, "confusion": {}}
