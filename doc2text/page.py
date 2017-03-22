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

    def maybe_rotate(self):
        infile = get_temp_filename("png")
        outfile = get_temp_filename("")
        cv2.imwrite(infile, self.original)

        pytesseract.pytesseract.run_tesseract(infile, outfile, config="-psm 0")

        theta = 0.
        for line in open(outfile+".osd","r").readlines():
            if "Rotate:" in line:
                theta = float(line.split(" ")[1])
        print(theta)
        return transformations.rotate(self.original, theta)


    def extract_text(self, lang):
        temp_filename = get_temp_filename('png')
        cv2.imwrite(temp_filename, self.processed)
        try:
            # pytesseract requires that language is passed as 3-letter code, lowercased.
            return pytesseract.image_to_string(Image.open(temp_filename), lang=lang.lower())
        except TypeError:
            # buggy pytesseract throws a TypeError when handling error messages from itself.
            logging.error('Tesseract error when calling tesseract')
        finally:
            os.remove(temp_filename)

    @property
    def processed(self):
        if not self._processed:
            rotated_image = self.maybe_rotate()
            cropped_image = transformations.process_image(rotated_image)
            self._processed = transformations.process_skew(cropped_image)
        return self._processed
