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


@pytest.mark.parametrize(
    "width, height, expected",
    [
        (51, 6, True),  # wide and tall enough
        (100, 100, True),
        (50, 6, False),  # width must be strictly > 50
        (51, 5, False),  # height must be strictly > 5
        (50, 5, False),
    ],
)
def test_is_elephant_rumble(width, height, expected):
    assert Boxing.is_elephant_rumble(width, height) is expected


def test_count_unique_rumbles_empty():
    assert Boxing.count_unique_rumbles([]) == []


def test_count_unique_rumbles_single():
    assert Boxing.count_unique_rumbles([(100, 300)]) == [(100, 300)]


def test_count_unique_rumbles_distinct_in_both_axes_counts_separately():
    # Differs in x by >= 20 AND in y by >= 200 -> two separate elephants.
    rumbles = [(0, 0), (100, 300)]
    assert Boxing.count_unique_rumbles(rumbles) == [(0, 0), (100, 300)]


def test_count_unique_rumbles_similar_frequency_merges():
    # x within 20 -> treated as the same elephant even if y is far apart.
    rumbles = [(0, 0), (10, 1000)]
    assert Boxing.count_unique_rumbles(rumbles) == [(0, 0)]


def test_count_unique_rumbles_similar_time_merges():
    # y within 200 -> merged even if x is far apart (the rule is an OR).
    rumbles = [(0, 0), (100, 50)]
    assert Boxing.count_unique_rumbles(rumbles) == [(0, 0)]


def test_count_unique_rumbles_boundaries_are_strict():
    # Exactly 20 apart in x and 200 apart in y is NOT similar (strict <).
    rumbles = [(0, 0), (20, 200)]
    assert Boxing.count_unique_rumbles(rumbles) == [(0, 0), (20, 200)]


def test_count_unique_rumbles_compares_against_all_counted():
    # The third rumble is distinct from the first but similar to the second,
    # so it is merged -> two unique elephants overall.
    rumbles = [(0, 0), (100, 300), (110, 305)]
    assert Boxing.count_unique_rumbles(rumbles) == [(0, 0), (100, 300)]


def test_thresholds_are_tunable():
    # Two rumbles that the defaults merge (y within 200) become distinct when
    # the time threshold is tightened -- proves the parameters are configurable.
    rumbles = [(0, 0), (100, 50)]
    assert Boxing.count_unique_rumbles(rumbles) == [(0, 0)]
    assert Boxing.count_unique_rumbles(
        rumbles, same_frequency_px=20, same_time_px=10
    ) == [(0, 0), (100, 50)]

    # A box rejected by the default width filter passes with a lower threshold.
    assert Boxing.is_elephant_rumble(40, 6) is False
    assert Boxing.is_elephant_rumble(40, 6, min_width=30) is True


def test_default_thresholds_unchanged():
    # Guard the calibrated defaults so a refactor cannot silently shift them.
    assert (Boxing.MIN_RUMBLE_WIDTH, Boxing.MIN_RUMBLE_HEIGHT) == (50, 5)
    assert (Boxing.SAME_FREQUENCY_PX, Boxing.SAME_TIME_PX) == (20, 200)
    assert (
        Boxing.ROI_TOP,
        Boxing.ROI_BOTTOM,
        Boxing.ROI_LEFT,
        Boxing.ROI_RIGHT,
    ) == (60, 425, 82, 570)
