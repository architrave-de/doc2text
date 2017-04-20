import pyocr

import cv2
import numpy as np
from PIL import Image

from . import transformations


def get_image_from_file(fd):
    image_array = np.asarray(bytearray(fd.read()), dtype=np.uint8)
    return cv2.imdecode(image_array, 0)


class Page(object):
    def __init__(self, file_descriptor, language=None):
        self.original = get_image_from_file(file_descriptor)
        self.language = language
        self.pyocr_tool = pyocr.get_available_tools()[0]
        self._processed = None

    def extract_text(self, language=None):
        image = Image.fromarray(self.processed)
        return self.pyocr_tool.image_to_string(image, lang=language or self.language)

    @property
    def original_orientation(self):
        image = Image.fromarray(self.original)
        return self.pyocr_tool.detect_orientation(image, lang=self.language)['angle']

    @property
    def processed(self):
        if not self._processed:
            rotated_image = transformations.rotate(self.original, self.original_orientation)
            cropped_image = transformations.process_image(rotated_image)
            self._processed = transformations.deskew(cropped_image)
            return self._processed
