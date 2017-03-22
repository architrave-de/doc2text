import os
import logging
import tempfile
import datetime

import cv2
import numpy as np
import pytesseract
from PIL import Image

from . import transformations


def get_cv_image_from_file(fd):
    image_array = np.asarray(bytearray(fd.read()), dtype=np.uint8)
    return cv2.imdecode(image_array, 0)


def get_temp_filename(extension):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    prefix = '{}_{}_'.format(__name__, timestamp)
    temp_file = tempfile.NamedTemporaryFile(prefix=prefix)
    return '{}.{}'.format(temp_file.name, extension)


class Page(object):
    def __init__(self, file_descriptor):
        self.original = get_cv_image_from_file(file_descriptor)
        self._processed = None

    def extract_text(self, lang, auto_rotate=False):
        config = "-psm 0" if auto_rotate else None
        temp_filename = get_temp_filename('png')
        cv2.imwrite(temp_filename, self.processed)
        try:
            # pytesseract requires that language is passed as 3-letter code, lowercased.
            return pytesseract.image_to_string(Image.open(temp_filename), lang=lang.lower(), config=config)
        except TypeError:
            # buggy pytesseract throws a TypeError when handling error messages from itself.
            logging.error('Tesseract error when calling tesseract')
        finally:
            os.remove(temp_filename)

    @property
    def processed(self):
        if not self._processed:
            cropped_image = transformations.process_image(self.original)
            self._processed = transformations.process_skew(cropped_image)
        return self._processed
