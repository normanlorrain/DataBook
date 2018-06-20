import io
import os
import tempfile

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab import rl_config
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from util import log

offset = 10
_filename = os.path.join(tempfile.gettempdir(), "~databook_temp.pdf")


def generateWatermarkPage(watermarkHeader, watermarkFooter, cropBox=None):
    if cropBox:
        x1, y1 = cropBox.lowerLeft
        x2, y2 = cropBox.upperRight
        log.debug(f"{(x2 -x1)}, {(y2-y1)}")
        landscapeMode = (x2 - x1) > (y2 - y1)
    else:  # simple watermark letter page
        x1, y1 = 0, 0
        landscapeMode = False

    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Oblique", 8)
    if landscapeMode:
        log.debug("========================  LANDSCAPE")
        can.rotate(-90)

        footerX = -int( (y1+y2) /2 )  # Think draw, then rotate
        footerY = int(x1 + offset)  # Think draw, then rotate
        headerX = -int( (y1+y2) /2 )  # Think draw, then rotate
        headerY = int(x2 - offset)  # Think draw, then rotate
    else:
        footerX = int( (x1+x2) / 2)
        footerY = int(y1 + offset)
        headerX = int( (x1+x2) / 2)
        headerY = int(y2 - offset)

    log.debug(f"drawstring: {footerX},{footerY}")
    can.drawCentredString(footerX, footerY, watermarkFooter)
    can.drawCentredString(headerX, headerY, watermarkHeader)
    can.showPage()
    can.save()
    # move to the beginning of the StringIO buffer
    packet.seek(0)
    pdfWatermark = PdfFileReader(packet)
    return pdfWatermark.getPage(0)


def generateMultipageWatermarkFile(watermarkFilename, watermark, target):
    if not target:
        c = canvas.Canvas(watermarkFilename, pagesize=letter)
        numPages = 1
    else:
        pdfInput = PdfFileReader(open(target, "rb"))
        numPages = pdfInput.getNumPages()
        mediaBox = pdfInput.getPage(0).cropBox
        log.debug(f"{watermarkFilename} - {mediaBox}")
        c = canvas.Canvas(
            watermarkFilename,
            bottomup=1,
            pageCompression=0,
            verbosity=0,
            encrypt=None,
            cropBox=mediaBox,
            artBox=mediaBox,
            trimBox=mediaBox,
            bleedBox=mediaBox,
        )

    for _ in range(numPages):
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(offset, offset, watermark)
        c.showPage()

    c.save()


def pdfPageList(filename):
    log.debug(f"============= {filename} ================")
    pdfInput = PdfFileReader(open(filename, "rb"))
    log.debug(f"getDocumentInfo:{pdfInput.getDocumentInfo()}")
    log.debug(f"fields {pdfInput.getFields()} ")
    try:
        log.debug(f"outlines {str(pdfInput.getOutlines())} ")
    except:
        pass
    log.debug(f"layout {pdfInput.getPageLayout()} ")
    log.debug(f"mode  {pdfInput.getPageMode()} ")
    for page in pdfInput.pages:
        log.debug(f"             ---- {filename}  page  -------------")
        log.debug(f"             media {page.mediaBox}")
        log.debug(f"             crop  {page.cropBox}")
        log.debug(f"             art   {page.artBox}")
        log.debug(f"             bleed {page.bleedBox}")
        log.debug(f"             trim  {page.trimBox} ")

        yield page


if __name__ == "__main__":
    import sys

    log.basicConfig(
        stream=sys.stdout,
        level=log.DEBUG,
        format="%(levelname)8s: " "%(filename)12s: " "%(lineno)4d:\t" "%(message)s",
    )

    log.info("testing PDF routines")

    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test"))
    # default arg
    _filename = ".single page letter.pdf"
    generateMultipageWatermarkFile("Text to watermark")

    # given letter
    _filename = ".single page letter2.pdf"
    generateMultipageWatermarkFile(
        "Text to watermark", os.path.join("single page letter.pdf")
    )

    # given B5
    _filename = ".single page B5.pdf"
    generateMultipageWatermarkFile(
        "Text to watermark", os.path.join("single page B5.pdf")
    )

    # given multipage letter
    _filename = ".multi page letter.pdf"
    generateMultipageWatermarkFile("10", os.path.join("multi page letter.pdf"))
