"""Offline evaluation and dataset-audit tools for the elephant counter.

This package is intentionally free of Flask, Azure, and audio/ML dependencies
so that it can be run by anyone with a checkout of the repository and no cloud
credentials.

Important limitation on "accuracy"
----------------------------------
The repository ships the *boxed output* images under
``data/spectrogram_bb/{0,1,2}/`` sorted into folders by the counting
algorithm's own predicted count. It does **not** ship the input spectrograms,
nor any human ground-truth elephant count per segment -- the source annotations
record call frequency and Cornell's "marginal" confidence tags, but (as the
project team noted) they "don't mention the number of elephants".

Therefore a true accuracy figure cannot be reproduced from this repository
alone. What these tools provide instead is:

* a reproducible audit of the shipped, already-predicted dataset, and
* a clean regeneration of the ``file_name,number_of_elephants`` labels.

If a ground-truth label set becomes available, ``score_predictions`` provides a
ready hook to compute real accuracy/precision/recall against it.
"""
