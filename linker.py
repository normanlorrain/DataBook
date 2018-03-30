from PyPDF2 import PdfFileWriter, PdfFileReader
import re
import os
import logging as log
import subprocess
import datetime
import pdf


class Linker:
    def __init__(self,  authoredFiles, referenceFiles, output):
        datestamp = datetime.date.today()

        self.build =  authoredFiles
        self.buildRef = referenceFiles
        self.datestamp = datestamp
        self.output = output
        self.outfile = os.path.join( output, f'ElmTree DataBook {datestamp}.pdf' )
        self.outfileReferences = os.path.join( self.output, f'ElmTree DataBook References {self.datestamp}.pdf' )
        self.outfileWithReferences = os.path.join( output, f'ElmTree DataBook {datestamp} With References.pdf' )

    def __enter__(self):
        return self
    def __exit__(self, exct_type, exce_value, traceback):
        log.info( 'cleaning up')
        if os.path.isfile(self.outfile):
            try:
                os.remove( self.outfile )
            except Exception as e:
                log.exception (e)


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
            watermarkText = f"{sectionNumber}.{documentNumber} {sectionName} - {documentName}                  ElmTree DataBook, {self.datestamp}, page {pageNumber}"

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
        outputPDFfile = open(self.outfile, "wb")
        pdfOutput.write(outputPDFfile)
        outputPDFfile.close()	


    # Watermarking is done in the compile stage for the references.
    def linkReferences(self, referenceFiles):
        fileList = ' '.join(map('"{0}"'.format, referenceFiles)) 
        log.debug(fileList)
        cmd = f'pdftk "{self.outfile}" attach_files {fileList} output "{self.outfileWithReferences}"'
        log.debug(cmd)
        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            log.exception (e)
