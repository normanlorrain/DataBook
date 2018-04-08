import datetime
import logging as log
import os
import re
import subprocess

from PyPDF2 import PdfFileReader, PdfFileWriter

import pdf


class Linker:
    def __init__(self,  authoredFiles, referenceFiles,title, output):
        datestamp = datetime.date.today()
        self.title = title
        self.build =  authoredFiles
        self.buildRef = referenceFiles
        self.datestamp = datestamp
        self.outfileNoReferences = os.path.join(self.build, '~databook_no_references.pdf' )
        self.outfileWithReferences = f'{output}'

    def __enter__(self):
        return self
    def __exit__(self, exct_type, exce_value, traceback):
        log.info( 'cleaning up')
        # if os.path.isfile(self.outfileNoReferences):
        #     try:
        #         os.remove( self.outfileNoReferences )
        #     except Exception as e:
        #         log.exception (e)


    def linkAuthored(self, authoredFiles):
        # pdfOutput PDF
        pdfOutput = PdfFileWriter()
        
        pageNumber = 0
        parentSection = None
        parentSectionNumber = None

        for original in authoredFiles:
            log.info(os.path.basename(original))
            match = re.match(r'(\d+)-(\d+)\s+\[(.*?)\]\s+\[(.*?)\].*', os.path.basename(original) )
            if(match):
                log.debug( f"{match.groups()}" )
            else:
                log.warn('SKIPPING - File name not right format: {} '.format( os.path.basename(original)))  #might be the output file from previous run
                continue
            sectionNumber = int(match.group(1))
            documentNumber = int(match.group(2))
            
            sectionName = match.group(3)
            documentName = match.group(4)
            watermarkText = f"{sectionNumber}.{documentNumber} {sectionName} - {documentName}                  {self.title}, {self.datestamp}, page {pageNumber}"

            bookmarkPage = pageNumber # Save this page number for the bookmark below
            for page in pdf.pdfPageList(original):
                if pageNumber > 0:
                    watermarkPage = pdf.generateWatermarkPage( watermarkText, page.cropBox )
                    page.mergePage(watermarkPage)
                pdfOutput.addPage(page)
                pageNumber+= 1

            if sectionNumber != parentSectionNumber:
                parentSectionNumber = sectionNumber
                parentSection = pdfOutput.addBookmark(sectionName, bookmarkPage, bold=True )
            else:
                pdfOutput.addBookmark(documentName, bookmarkPage, parentSection )


        # finally, write "pdfOutput" to a real file
        log.debug(f'linking authored files into {self.outfileNoReferences}')
        outputPDFfile = open(self.outfileNoReferences, "wb")
        pdfOutput.write(outputPDFfile)
        outputPDFfile.close()	


    # Watermarking is done in the compile stage for the references.
    def linkReferences(self, referenceFiles):
        log.debug(f'linkReferences()')
        fileList = ' '.join(map('"{0}"'.format, referenceFiles)) 
        log.debug(fileList)
        cmd = f'pdftk "{self.outfileNoReferences}" attach_files {fileList} output "{self.outfileWithReferences}"'
        log.debug(cmd)
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            log.exception (e)
            raise
