import pyocr

import cv2
import numpy as np
from PIL import Image

from . import transformations


def get_cv_image_from_file(fd):
    image_array = np.asarray(bytearray(fd.read()), dtype=np.uint8)
    return cv2.imdecode(image_array, 0)


def cv_to_pil(cv_im):
    return Image.fromarray(cv_im)


class Page(object):
    def __init__(self, file_descriptor):
        self.original = get_cv_image_from_file(file_descriptor)
        self.pyocr_tool = pyocr.get_available_tools()[0]
        self._processed = None

    def maybe_rotate(self):
        image = cv_to_pil(self.original)
        try:
            rotation_degree = self.pyocr_tool.detect_orientation(image, lang='deu')['angle']
        except:
            rotation_degree = 0.
        theta = rotation_degree
        return transformations.rotate(self.original, theta)

    def extract_text(self, lang):
        image = cv_to_pil(self.processed)
        try:
            text = self.pyocr_tool.image_to_string(image, lang=lang)
        except:
            text = None
        return text

    @property
    def processed(self):
        if not self._processed:
            rotated_image = self.maybe_rotate()
            cropped_image = transformations.process_image(rotated_image)
            self._processed = transformations.process_skew(cropped_image)
        return self._processed
