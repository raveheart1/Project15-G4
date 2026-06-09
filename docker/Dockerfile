FROM python:3.11-slim

ARG WORKING_DIR=/usr/src/app

WORKDIR $WORKING_DIR


RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    nano \
    libsndfile1 \
    build-essential \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Install the package with the runtime extras (audio pipeline, optional CNN,
# and cloud integrations). The core install alone omits these heavy stacks.
RUN pip install . --disable-pip-version-check --no-cache-dir \
    && pip install ".[audio,ml,cloud]" --disable-pip-version-check --no-cache-dir

CMD ["python3"]