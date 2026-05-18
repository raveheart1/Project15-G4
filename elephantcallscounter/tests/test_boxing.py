import pandas as pd
import pytest

from elephantcallscounter.data_analysis.boxing import Boxing

pytestmark = pytest.mark.unit


def test_write_labels_to_csv_file_writes_file_names_and_counts(tmp_path):
    csv_file = tmp_path / "labels.csv"
    boxing = Boxing("", "", str(csv_file), monochrome=None)
    dataset = pd.DataFrame(
        [
            ("mono_nn01d.png", 2),
            ("mono_nn01b.png", 1),
        ]
    )

    boxing.write_labels_to_csv_file(dataset)

    labels = pd.read_csv(csv_file)
    assert labels.to_dict("records") == [
        {"file_name": "mono_nn01d.png", "number_of_elephants": 2},
        {"file_name": "mono_nn01b.png", "number_of_elephants": 1},
    ]
