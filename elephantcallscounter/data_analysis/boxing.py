import logging
import math
import os
from typing import List, Tuple

from elephantcallscounter.utils.path_utils import get_project_root, join_paths

logger = logging.getLogger(__name__)

Point = Tuple[int, int]


class Boxing:
    # --- Tunable parameters for the rule-based counter ---------------------
    # These were originally hard-coded magic numbers. They are calibrated for
    # the 640x480 spectrograms produced by this pipeline; changing the
    # spectrogram geometry, frequency range, or time axis will require
    # re-tuning them (see the "Further Research" notes in the project docs).

    # A bounding box is only treated as a rumble if it is wider/taller than:
    MIN_RUMBLE_WIDTH = 50
    MIN_RUMBLE_HEIGHT = 5
    # Two rumble centres belong to the same elephant when their horizontal
    # distance (similar base frequency) OR vertical distance (similar mean
    # time) falls below these pixel thresholds:
    SAME_FREQUENCY_PX = 20
    SAME_TIME_PX = 200
    # Region of interest used to crop the plot axes off a 640x480 spectrogram:
    ROI_TOP = 60
    ROI_BOTTOM = 425
    ROI_LEFT = 82
    ROI_RIGHT = 570

    def __init__(
        self, image_folder, target_folder, csv_file_path, monochrome, write_file=False
    ):
        self.image_folder = image_folder
        self.target_folder = target_folder
        self.csv_file_path = csv_file_path
        self.monochrome = monochrome
        self.write_file = write_file

    @staticmethod
    def is_elephant_rumble(
        width: int,
        height: int,
        min_width: int = MIN_RUMBLE_WIDTH,
        min_height: int = MIN_RUMBLE_HEIGHT,
    ) -> bool:
        """Whether a bounding box is large enough to be a candidate rumble.

        Boxes that are too short or too narrow are treated as noise rather
        than elephant rumbles.

        :param int width:
        :param int height:
        :param int min_width: minimum width to qualify (default MIN_RUMBLE_WIDTH)
        :param int min_height: minimum height to qualify (MIN_RUMBLE_HEIGHT)
        :return bool:
        """
        return height > min_height and width > min_width

    @staticmethod
    def count_unique_rumbles(
        rumbles: List[Point],
        same_frequency_px: int = SAME_FREQUENCY_PX,
        same_time_px: int = SAME_TIME_PX,
    ) -> List[Point]:
        """Deduplicate rumble centre points into unique elephants.

        Two rumbles are considered to come from the same elephant when they
        share a similar base frequency (x within ``same_frequency_px``) or a
        similar mean time (y within ``same_time_px``). Rumbles are processed in
        order and a rumble that is similar to any already-counted elephant is
        skipped.

        :param list rumbles: list of ``(x, y)`` rumble centre points
        :param int same_frequency_px: horizontal merge threshold in pixels
        :param int same_time_px: vertical merge threshold in pixels
        :return list: the unique elephant centre points, in first-seen order
        """
        elephants = []
        for rumble in rumbles:
            similar_rumbles = [
                elephant
                for elephant in elephants
                if (abs(elephant[0] - rumble[0]) < same_frequency_px)
                or (abs(elephant[1] - rumble[1]) < same_time_px)
            ]
            if len(similar_rumbles) < 1:
                elephants.append(rumble)
        return elephants

    def write_box_to_file(self, image, elephants, image_filename):
        import cv2

        image_filename = image_filename.replace("mono_", "boxed_")
        os.makedirs(
            join_paths([self.target_folder, str(len(elephants))]), exist_ok=True
        )
        boxed_path = join_paths(
            [self.target_folder, str(len(elephants)), image_filename]
        )
        cv2.imwrite(boxed_path, image)
        logger.info(f"Boxed image stored as {boxed_path}")

    def create_boxes(self, image_filename):
        import cv2

        logger.info(f"Creating boxes for {self.image_folder + image_filename}...")

        image = self.monochrome.create_monochrome(
            join_paths([get_project_root(), self.image_folder, image_filename])
        )

        # cut off the axes (source images are 640 x 480 pixels)
        y_top = self.ROI_TOP
        y_bottom = self.ROI_BOTTOM
        x_left = self.ROI_LEFT
        x_right = self.ROI_RIGHT
        ROI = image[y_top:y_bottom, x_left:x_right]

        thresh_inverse = cv2.bitwise_not(ROI)

        # create contours
        contours, hierarchy = cv2.findContours(
            thresh_inverse, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(ROI, contours, -1, (0, 255, 0), 1)

        # approximate contours to polygons + get bounding rects
        boxes = [None] * len(contours)

        elephant_rumbles = []

        for i, c in enumerate(contours):
            polygon = cv2.approxPolyDP(c, 3, True)
            boxes[i] = cv2.boundingRect(polygon)
            # (x, y, w, h), where x, y is the top left corner,
            # and w, h are the width and height respectively

            rect = boxes[i]
            width = rect[2]
            height = rect[3]

            # check if this can be an elephant
            if self.is_elephant_rumble(width, height):
                middle_x = math.floor(rect[0] + (width / 2))
                middle_y = math.floor(rect[1] + (height / 2))

                cv2.rectangle(
                    ROI,
                    (int(boxes[i][0]), int(boxes[i][1])),
                    (int(boxes[i][0] + boxes[i][2]), int(boxes[i][1] + boxes[i][3])),
                    cv2.COLOR_BGR2HSV,
                    2,
                )

                elephant_rumbles.append((middle_x, middle_y))

        # count the elephants by deduplicating rumbles that likely belong to
        # the same animal
        elephants = self.count_unique_rumbles(elephant_rumbles)
        for rumble in elephants:
            logger.info(f"Unique elephant at {rumble}")
            cv2.drawMarker(ROI, rumble, cv2.COLOR_LAB2LBGR, markerType=cv2.MARKER_STAR)

        logger.info(f"Found {len(elephants)} elephant(s) in image!")

        # put the ROI on top of the original image
        h, w = ROI.shape[0], ROI.shape[1]
        image[y_top : y_top + h, x_left : x_left + w] = ROI

        if self.write_file:
            self.write_box_to_file(image, elephants, image_filename)

        return image, len(elephants)

    def write_labels_to_csv_file(self, dataset):
        labels = dataset.copy()
        labels.columns = ["file_name", "number_of_elephants"]
        labels.to_csv(self.csv_file_path, index=False)
