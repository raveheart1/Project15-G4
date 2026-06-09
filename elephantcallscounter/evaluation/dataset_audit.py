"""Audit and (re)build labels for the boxed spectrogram dataset.

Run directly, with no cloud credentials required::

    # Print the class distribution of the shipped boxed dataset
    python -m elephantcallscounter.evaluation.dataset_audit summarize

    # Check the committed labels CSV against the folder structure
    python -m elephantcallscounter.evaluation.dataset_audit audit

    # Regenerate a clean file_name,number_of_elephants labels CSV
    python -m elephantcallscounter.evaluation.dataset_audit rebuild-labels
"""
import argparse
import csv
import os
from collections import Counter, OrderedDict

# Default locations relative to the package, so the tool works from any CWD.
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BOXED_DIR = os.path.join(_PACKAGE_ROOT, "data", "spectrogram_bb")
DEFAULT_LABELS_CSV = os.path.join(
    _PACKAGE_ROOT, "data", "labels", "spec_images_labels.csv"
)

# Boxed images are stored under one subfolder per predicted count.
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def _is_count_folder(name):
    return name.isdigit()


def iter_boxed_labels(boxed_dir=DEFAULT_BOXED_DIR):
    """Yield ``(file_name, number_of_elephants)`` for every boxed image.

    The predicted count is taken from the name of the subfolder the image
    lives in (``spectrogram_bb/2/foo.png`` -> count 2).

    :param str boxed_dir: directory containing ``0/``, ``1/``, ... subfolders
    :return: generator of ``(str, int)`` pairs, sorted for determinism
    """
    if not os.path.isdir(boxed_dir):
        raise FileNotFoundError("boxed dataset directory not found: %s" % boxed_dir)

    rows = []
    for entry in sorted(os.listdir(boxed_dir)):
        sub = os.path.join(boxed_dir, entry)
        if not (os.path.isdir(sub) and _is_count_folder(entry)):
            continue
        count = int(entry)
        for file_name in sorted(os.listdir(sub)):
            if file_name.lower().endswith(IMAGE_EXTENSIONS):
                rows.append((file_name, count))
    return iter(rows)


def summarize_boxed_dataset(boxed_dir=DEFAULT_BOXED_DIR):
    """Return an ordered ``{predicted_count: number_of_images}`` summary.

    :param str boxed_dir:
    :return collections.OrderedDict:
    """
    counter = Counter(count for _name, count in iter_boxed_labels(boxed_dir))
    return OrderedDict(sorted(counter.items()))


def build_labels(boxed_dir=DEFAULT_BOXED_DIR):
    """Return a clean list of ``(file_name, number_of_elephants)`` rows.

    :param str boxed_dir:
    :return list[tuple[str, int]]:
    """
    return list(iter_boxed_labels(boxed_dir))


def write_labels_csv(rows, csv_path=DEFAULT_LABELS_CSV):
    """Write rows to a tidy ``file_name,number_of_elephants`` CSV.

    Uses the stdlib csv writer rather than a DataFrame dump, which is what
    corrupted the previously committed labels file.

    :param list[tuple[str, int]] rows:
    :param str csv_path:
    :return int: number of label rows written
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file_name", "number_of_elephants"])
        writer.writerows(rows)
    return len(rows)


def audit_labels_csv(csv_path=DEFAULT_LABELS_CSV, boxed_dir=DEFAULT_BOXED_DIR):
    """Compare a labels CSV against the boxed folder structure.

    :param str csv_path:
    :param str boxed_dir:
    :return dict: report with ``valid``, ``malformed_rows``, ``missing``
        (in folders but not the CSV), ``extra`` (in the CSV but not folders)
        and ``mismatched`` (count disagrees) entries.
    """
    expected = dict(iter_boxed_labels(boxed_dir))

    found = {}
    malformed_rows = 0
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as handle:
            reader = csv.DictReader(handle)
            has_columns = reader.fieldnames and {
                "file_name",
                "number_of_elephants",
            } <= set(reader.fieldnames)
            if has_columns:
                for row in reader:
                    try:
                        found[row["file_name"]] = int(row["number_of_elephants"])
                    except (TypeError, ValueError):
                        malformed_rows += 1
            else:
                # Header itself is wrong/corrupt: treat every data row as bad.
                malformed_rows = sum(1 for _ in reader)

    missing = sorted(name for name in expected if name not in found)
    extra = sorted(name for name in found if name not in expected)
    mismatched = sorted(
        name
        for name in expected
        if name in found and found[name] != expected[name]
    )

    return {
        "valid": (
            malformed_rows == 0 and not missing and not extra and not mismatched
        ),
        "malformed_rows": malformed_rows,
        "missing": missing,
        "extra": extra,
        "mismatched": mismatched,
        "expected_total": len(expected),
        "found_total": len(found),
    }


def score_predictions(predictions, ground_truth):
    """Hook for real accuracy scoring once ground-truth counts are available.

    :param dict predictions: ``{file_name: predicted_count}``
    :param dict ground_truth: ``{file_name: true_count}``
    :return dict: ``accuracy`` plus the raw confusion ``(true, pred): n`` map,
        computed over the file names present in both inputs.
    """
    shared = sorted(set(predictions) & set(ground_truth))
    if not shared:
        return {"accuracy": None, "n": 0, "confusion": {}}

    correct = 0
    confusion = Counter()
    for name in shared:
        true_count = ground_truth[name]
        pred_count = predictions[name]
        confusion[(true_count, pred_count)] += 1
        if true_count == pred_count:
            correct += 1
    return {
        "accuracy": correct / len(shared),
        "n": len(shared),
        "confusion": dict(confusion),
    }


def _cmd_summarize(args):
    summary = summarize_boxed_dataset(args.boxed_dir)
    total = sum(summary.values())
    print("Boxed spectrogram dataset: %s" % args.boxed_dir)
    for count, n in summary.items():
        print("  %d elephant(s): %5d images" % (count, n))
    print("  %-13s %5d images" % ("total:", total))


def _cmd_audit(args):
    report = audit_labels_csv(args.labels_csv, args.boxed_dir)
    print("Auditing %s against %s" % (args.labels_csv, args.boxed_dir))
    print("  images in folders : %d" % report["expected_total"])
    print("  rows in labels CSV: %d" % report["found_total"])
    print("  malformed rows    : %d" % report["malformed_rows"])
    print("  missing from CSV  : %d" % len(report["missing"]))
    print("  extra in CSV      : %d" % len(report["extra"]))
    print("  count mismatches  : %d" % len(report["mismatched"]))
    print("  VALID" if report["valid"] else "  INVALID -> run rebuild-labels")
    return 0 if report["valid"] else 1


def _cmd_rebuild_labels(args):
    rows = build_labels(args.boxed_dir)
    written = write_labels_csv(rows, args.labels_csv)
    print("Wrote %d clean label rows to %s" % (written, args.labels_csv))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boxed-dir", default=DEFAULT_BOXED_DIR)
    parser.add_argument("--labels-csv", default=DEFAULT_LABELS_CSV)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("summarize").set_defaults(func=_cmd_summarize)
    sub.add_parser("audit").set_defaults(func=_cmd_audit)
    sub.add_parser("rebuild-labels").set_defaults(func=_cmd_rebuild_labels)

    args = parser.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
