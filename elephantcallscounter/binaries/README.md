# Model binaries

Trained model artifacts (e.g. `resnet_25_epoch/`, `vgg_5_epoch/`) are **not
committed** to this repository — they are large and reproducible from the
training data. This directory is kept under version control via `.gitkeep` so
the code that reads/writes models here has a stable target path.

## How the pipeline uses this directory

`elephantcallscounter/services/data_analysis_service.py::run_cnn` and the
`ElephantCounterResnet` / `ElephantCounterVGG` classes load and save models
relative to the project root, i.e. `elephantcallscounter/binaries/`.

The demo pipeline (`pipeline_services.pipeline_run`) treats the CNN as an
**optional** classifier:

- The rule-based boxing algorithm always produces an elephant count per
  spectrogram (this is the project's primary counting method).
- If a trained CNN model is present in this directory, its predictions
  override the rule-based counts. If no model is found, the pipeline logs a
  message and falls back to the boxing counts, so it still runs end-to-end.

## Producing a model

Train a ResNet50 (default) or VGG16 classifier from a directory of boxed
spectrograms split into `train/`, `val/` (ResNet) or `valid/` (VGG), and
`test/` subfolders, each containing `0/`, `1/`, `2/` class folders:

```bash
flask data_analysis train_cnn data/spectrogram_bb binaries/resnet_
flask data_analysis train_vgg_cnn data/spectrogram_bb
```

The resulting model is saved here and can then be used for inference:

```bash
flask data_analysis run_cnn binaries/resnet data/demo/spectrogram_bb
```
