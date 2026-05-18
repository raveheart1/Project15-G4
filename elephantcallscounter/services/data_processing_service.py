def create_file_segments(file_name, training_set=None, crop_set=None):
    from elephantcallscounter.data_processing.metadata_processing import (
        MetadataProcessing,
    )
    from elephantcallscounter.data_processing.segment_files import SegmentFiles

    metadata = MetadataProcessing(metadata_filepath=file_name)
    segment_files = SegmentFiles(False, training_set=training_set, crop_set=crop_set)
    segment_files.process_segments(
        segment_files.ready_file_segments(metadata.load_metadata())
    )
