import mimetypes
from io import BytesIO

import PyPDF2 as pyPdf
from wand.image import Image

from .page import Page

IMAGE_MIMETYPES = [
    'image/bmp', 'image/png', 'image/tiff', 'image/jpeg',
    'image/jpg', 'video/JPEG', 'video/jpeg2000'
]

PDF_MIMETYPE = 'application/pdf'


class FileNotAcceptedException(Exception):
    message = 'File type unsupported. Only images (bitmaps, PNG, JPEG) and PDF'


class Document(object):
    CONVERSION_RESOLUTION = 300
    COMPRESSION_QUALITY = 99

    def get_text(self, language):
        raise NotImplementedError()

    def __init__(self, path, language=None):
        self.prepared = False
        self.path = path
        self.language = language
        self._pages = []

    def _convert(self, source_fd, destination_fd):
        with Image(file=source_fd, resolution=self.CONVERSION_RESOLUTION) as image:
            image.format = 'png'
            image.compression_quality = self.COMPRESSION_QUALITY
            image.save(file=destination_fd)

    def _preprocess(self):
        pass

    def prepare(self):
        self._preprocess()
        self.prepared = True

    @property
    def pages(self):
        return self._pages

    @staticmethod
    def get_by_path(path, language=None):
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type == PDF_MIMETYPE:
            return PDFDocument(path, language=language)
        elif mime_type in IMAGE_MIMETYPES:
            return ImageDocument(path, language=language)
        else:
            raise FileNotAcceptedException()


class ImageDocument(Document):
    def __init__(self, path, language=None):
        super(ImageDocument, self).__init__(path, language=language)
        self._page = None

    @property
    def pages(self):
        return [self._page] if self._page else []

    def get_text(self, language=None):
        if not self.prepared:
            self.prepare()
        return self._page.extract_text(language=language)

    def _preprocess(self):
        out_buffer = BytesIO()
        with open(self.path, 'rb') as f:
            self._convert(f, out_buffer)
            out_buffer.seek(0)
            self._page = Page(out_buffer, language=self.language)


class PDFDocument(Document):
    def get_text(self, language=None):
        lang = language or self.language
        if not self.prepared:
            self.prepare()
        return '\f'.join([(p.extract_text(language=lang) or '') for p in self._pages])

    def _preprocess(self):
        with open(self.path, 'rb') as pdf_file:
            pdf_reader = pyPdf.PdfFileReader(pdf_file)
            for i in range(pdf_reader.numPages):
                output = pyPdf.PdfFileWriter()
                output.addPage(pdf_reader.getPage(i))
                pdf_page_buffer = BytesIO()
                image_buffer = BytesIO()
                output.write(pdf_page_buffer)
                pdf_page_buffer.seek(0)
                self._convert(pdf_page_buffer, image_buffer)
                image_buffer.seek(0)
                self._pages.append(Page(image_buffer, language=self.language))
