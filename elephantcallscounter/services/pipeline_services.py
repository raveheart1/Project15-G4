import logging

import requests

from elephantcallscounter.services.data_analysis_service import (
    analyse_sound_data,
    create_mono_spectrograms,
    find_elephants_in_images,
    run_cnn,
)
from elephantcallscounter.utils.file_utils import get_files_in_dir
from elephantcallscounter.utils.path_utils import get_project_root, join_paths

logger = logging.getLogger(__name__)


def pipeline_run(
    folder_path,
    csv_file_path,
    publish_results=True,
    api_base_url="http://0.0.0.0:5000",
):
    for file in get_files_in_dir(folder_path):
        analyse_sound_data(
            file_path=join_paths([folder_path, file]),
            dest_path=join_paths([get_project_root(), "data/demo/spectrogram"]),
        )
    spectrogram_files_full = [
        join_paths([get_project_root(), "data/demo/spectrogram", file])
        for file in get_files_in_dir("data/demo/spectrogram")
    ]
    create_mono_spectrograms(
        spectrogram_files_full,
        target_folder=join_paths([get_project_root(), "data/demo/spectrogram_mono"]),
        write_file=True,
    )
    find_elephants_in_images(
        join_paths([get_project_root(), "data/demo/spectrogram_mono"]),
        join_paths([get_project_root(), "data/demo/spectrogram_bb"]),
        join_paths([get_project_root(), csv_file_path]),
    )
    value = run_cnn("binaries/resnet", "data/demo/spectrogram_bb")
    for index, file_path in enumerate(get_files_in_dir(folder_path)):
        if not publish_results:
            continue

        file_name = file_path.split("/")[-1]
        device_id = file_name.split("_")[0]
        URL = api_base_url.rstrip("/") + "/elephants/add_elephant_count/"
        requests.get(
            url=URL,
            params={
                "latitude": "20",
                "longitude": "30",
                "start_time": "2020-01-10 06:30:23",
                "end_time": "2021-01-11 06:30:23",
                "device_id": device_id,
                "number_of_elephants": value[index],
            },
        )
        logger.info("Number of elephants found after running pipeline %s", str(value))

    return value
