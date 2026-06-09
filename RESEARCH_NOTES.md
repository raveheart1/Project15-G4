# Research notes & improvement directions

This document captures the scientific state of the counter and where the
biggest gains likely are. It is aimed at anyone (including external
contributors without cloud access) who wants to improve the *quality* of the
counting, not just the engineering.

## Two counting methods

1. **Rule-based "boxing" (the production path).** A spectrogram is reduced to a
   monochrome image, contours are detected, bounding boxes are filtered by
   size, and overlapping boxes are merged into unique elephants. This is what
   actually produces the counts. The logic now lives in testable, documented
   form in `elephantcallscounter/data_analysis/boxing.py`:
   `is_elephant_rumble` and `count_unique_rumbles`.

2. **CNN classifier (optional, currently unused).** ResNet50 / VGG16 transfer
   learning that classifies a boxed spectrogram into 0 / 1 / 2 elephants
   (`elephantcallscounter/models/`). No trained weights are committed.

## Calibrated parameters (previously magic numbers)

The boxing rules are tuned to the **640x480** spectrograms this pipeline
produces. They are now named class attributes on `Boxing` so their effect can
be measured rather than guessed:

| Parameter            | Default | Meaning                                        |
|----------------------|---------|------------------------------------------------|
| `MIN_RUMBLE_WIDTH`   | 50 px   | a box narrower than this is noise              |
| `MIN_RUMBLE_HEIGHT`  | 5 px    | a box shorter than this is noise               |
| `SAME_FREQUENCY_PX`  | 20 px   | x-distance below which rumbles share a frequency|
| `SAME_TIME_PX`       | 200 px  | y-distance below which rumbles share a time     |
| `ROI_{TOP,BOTTOM,LEFT,RIGHT}` | 60/425/82/570 | crop that removes the plot axes |

Note the merge rule is an **OR**: two rumbles are treated as the same elephant
if they are close in frequency *or* in time. Widening or narrowing these
directly trades false merges against false splits.

## The accuracy-measurement gap (most important)

The original 97% figure was evaluated externally by Cornell and **cannot be
reproduced from this repository**: the shipped data is only the algorithm's own
boxed output (`data/spectrogram_bb/{0,1,2}/`), and the source annotations do
not record a ground-truth elephant count per segment.

Highest-leverage contribution: obtain or construct a small **ground-truth
labelled set** (segment -> true count), then wire it into
`elephantcallscounter.evaluation.dataset_audit.score_predictions`, which already
computes accuracy and a confusion matrix. Without this, *any* change to the
parameters above is unmeasurable.

## Suggested directions (from the project's own "Further Research")

- Fix the time axis in the spectrograms so `ROI_*` and `SAME_TIME_PX` are
  stable across files.
- Widen the analysed frequency range (currently ~10-50 Hz low/high-pass).
- Try better noise reduction before thresholding.
- Each of these should be evaluated through the `score_predictions` hook on a
  ground-truth set, comparing against the current defaults as a baseline.

## Recommendation on the CNN

The CNN is **trainable today** from the shipped class folders (they are exactly
the `train/val/test -> 0/1/2` layout the model expects):

```bash
pip install ".[audio,ml]"
flask data_analysis train_cnn data/spectrogram_bb binaries/resnet_
```

However, with no independent ground truth, a trained CNN would only be learning
to reproduce the rule-based labels, so it cannot be shown to be *more accurate*
than the rules it was trained on. Recommendation: **either** invest in a
ground-truth set and then compare CNN vs rules fairly, **or** remove the model
code to reduce confusion. Until one of those happens, the rule-based path
should remain the single source of truth (the pipeline already falls back to it
when no model is present).
