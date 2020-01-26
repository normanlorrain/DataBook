import datetime
import os
import re
import subprocess

from PyPDF2 import PdfFileWriter

from .util.config import config
from .util import log
from . import pdf


class Linker:
    def __init__(self):
        self.outfileNoReferences = os.path.join(
            config.build, "~databook_no_references.pdf"
        )

    def linkAuthored(self, authoredFiles):
        # pdfOutput PDF
        pdfOutput = PdfFileWriter()

        pdfPageNumber = 0
        pdfParentSection = None
        previousSectionNumber = None

        for original in authoredFiles:
            log.info(os.path.basename(original))
            match = re.match(
                r"(\d+)-(\d+)\s+\[(.*?)\]\s+\[(.*?)\].*", os.path.basename(original)
            )
            if match:
                log.debug(f"{match.groups()}")
            else:
                log.warn(
                    "SKIPPING - File name not right format: {} ".format(
                        os.path.basename(original)
                    )
                )  # might be the output file from previous run
                continue

            sectionNumber = int(match.group(1))
            documentNumber = int(match.group(2))
            sectionName = match.group(3)
            documentName = match.group(4)

            docPageNumber = 0
            for page in pdf.pdfPageList(original):
                pdfPageNumber += 1
                docPageNumber += 1

                if sectionNumber > 0:
                    log.debug(
                        f"Watermark for: {sectionNumber} - {sectionName}  pdf page: {pdfPageNumber}  doc page: {docPageNumber}"
                    )
                    watermarkHeader = f"{sectionNumber}.{documentNumber} {sectionName} - {documentName}"
                    watermarkFooter = (
                        f"{config.title}, {config.datestamp}, page {pdfPageNumber}"
                    )
                    watermarkPage = pdf.generateWatermarkPage(
                        watermarkHeader, watermarkFooter, page.cropBox
                    )
                    page.mergePage(watermarkPage)
                else:
                    log.debug("Watermak skipped for section 0")

                pdfOutput.addPage(page)

            log.debug(
                f"Bookmarks for section: {sectionName} - {documentName} pdf: {pdfPageNumber}  doc: {docPageNumber}"
            )
            if sectionNumber != previousSectionNumber:
                previousSectionNumber = sectionNumber
                pdfParentSection = pdfOutput.addBookmark(
                    sectionName, pdfPageNumber - docPageNumber, bold=True
                )
            pdfOutput.addBookmark(
                documentName, pdfPageNumber - docPageNumber, pdfParentSection
            )

        # finally, write "pdfOutput" to a real file
        log.debug(f"linking authored files into {self.outfileNoReferences}")
        outputPDFfile = open(self.outfileNoReferences, "wb")
        pdfOutput.write(outputPDFfile)
        outputPDFfile.close()

    # Watermarking is done in the compile stage for the references.

    def linkReferences(self, referenceFiles):
        log.debug(f"linkReferences()")
        fileList = " ".join(map('"{0}"'.format, referenceFiles))
        log.debug(fileList)
        cmd = f'pdftk "{self.outfileNoReferences}" attach_files {fileList} output "{config.output}"'
        log.debug(cmd)
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            log.exception(e)
            raise
