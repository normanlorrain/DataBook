import subprocess
from os.path import dirname, realpath, join
import os
import os.path
import re
import shutil
import glob
import logging as log
import datetime
import tempfile
import pdf
import contents
import dependency




class Compiler:
    def __init__(self, root, build, buildRef, output, clean = False):

        self.root = root
        self.build = build
        self.buildRef = buildRef
        self.contents = contents.Contents()
        self.datestamp = datetime.date.today()


        


    # Pandoc offers following PDF support:
    #     pdflatex   lualatex   xelatex :   all the same.  boring old LateX, but lots of flexibility.  See metadata.yaml.
    #     wkhtmltopdf:  ugly layout
    #     weasyprint: won't install on my python
    #     prince: works, but has small icon on first page.  Won't to page breaks.
    #     context: broken
    #     pdfroff: not available on Windows
    def compileMarkdown(self,directory, src,tgt):
        src = join(directory, src)
        tgt = join(self.build, tgt)

        metadata = join(self.root, 'metadata.yaml' )
        cmd = f'pandoc "{src}" "{metadata}" --metadata=date:{self.datestamp} --pdf-engine=pdflatex -o "{tgt}"'
        log.debug(cmd)
        try:
            subprocess.run(cmd, check = True)
        except:
            log.exception ( f"Call to pandoc failed.")
            raise







    def getSectionNumber(self,  path):
        #log.debug('getSectionNumber: ', path)
        match = re.match(r'.*?#(\d+).*', path)
        if(match):
            return int(match.group(1))
        else:
            return 0

    def getSectionName(self,  path):
        # log.debug('getSectionName: ', path)
        match = re.match(r'.*?#(\d+)(.*)', path)
        if(match):
            # log.debug(match.groups())
            name = match.group(2).strip()
            # log.debug('name:',name)
            return name
        else:
            raise Exception("can't get name")




    def createTOC(self):
        with open(join(self.build, ".toc.md" ), 'w') as f:
            f.write(contents.header)
            for line in self.contents.markdownLines():
                f.write(line)
            f.write("\n\n")
        self.compileMarkdown( self.build, ".toc.md", "00-01 [Intro] [Table of Contents].pdf" )

        
    def processMarkdown(self,sectionNumber, sectionName, directory, markdownFiles):
        for f in markdownFiles:
            match = re.match(r'#(\d+)(.*?)\.md',f)
            if match:
                number = int(match.group(1))
                name =  match.group(2).strip()
                log.info( f'    {f} (markdown file)')
                self.compileMarkdown( directory, f, f"{sectionNumber:02}-{number:02} [{sectionName}] [{name}].pdf" )
                self.contents.addSubSection(sectionNumber, number, name )
            else:
                log.warn(f'wrong format: {f} ')


    def processPreparedFiles( self, sectionNumber, sectionName, directory, preparedFiles ):
        for filename in preparedFiles:
            match = re.match(r'#(\d+)\&(.*?)\.pdf',filename)
            if match:
                number = int(match.group(1))
                name =  match.group(2).strip()
                log.info(f'    {filename} (prepared PDF file)')
                src = join(directory,filename)
                dst = join(self.build, f"{sectionNumber:02}-{number:02} [{sectionName}] [{name}].pdf" )
                shutil.copy(src, dst)
                self.contents.addSubSection(sectionNumber, number, name )


                dependency.check( directory, filename)



            else:
                log.warn(f'wrong format: {filename} ')

    def processDirectFiles(self,  sectionNumber, sectionName, directory, directFiles ):
            for filename in directFiles:
                match = re.match(r'#(\d+)\%(.*?)\.pdf',filename)
                if match:
                    number = int(match.group(1))
                    name =  match.group(2).strip()
                    log.info(f'    {filename} (directly edited PDF)')
                    src = join(directory,filename)
                    dst = join(self.build, f"{sectionNumber:02}-{number:02} [{sectionName}] [{name}].pdf" )
                    shutil.copy(src, dst)
                    self.contents.addSubSection(sectionNumber, number, name )
                else:
                    log.warn(f'wrong format: {filename} ')

    def processDownloadFiles(self, sectionNumber, sectionName, directory, downloadFiles ):
        for srcFile in downloadFiles:
            match = re.match(r'#(\d+)\$(.*?)\.pdf',srcFile)
            if match:
                documentNumber = int(match.group(1))
                documentName =  match.group(2).strip()
                log.info(f'    {srcFile} (reference document/attachment)')
                watermarkText = f"REFERENCE DOCUMENT:  {sectionNumber}.{documentNumber} {sectionName} - {documentName}                  ElmTree DataBook, {self.datestamp} "
                watermarkPdf = os.path.join(tempfile.gettempdir(),'~databook_temp.pdf' )
                pdf.generateMultipageWatermarkFile( watermarkPdf, watermarkText, os.path.join( directory, srcFile ) )

                # src = join(directory,srcFile)
                dst = join(self.buildRef, f"{sectionNumber:02}-{documentNumber:02} {sectionName}-{documentName}.pdf" )
                # shutil.copy(src, dst)
                self.contents.addSubSection(sectionNumber, documentNumber, documentName+' (Attachment)' )


                cmd = f'pdftk "{join(directory,srcFile)}" multistamp "{watermarkPdf}" output "{dst}"'
                log.debug(cmd)
                try:
                    subprocess.run(cmd, check=True)
                except Exception as e:
                    log.exception (e)
                    raise


            else:
                log.warn(f'Filename is in wrong format: {srcFile} ')




    def processFiles( self, directory, files):
        log.debug(f'{directory}:{files}')

        sectionNumber = self.getSectionNumber(directory)
        sectionName = self.getSectionName(directory)

        self.contents.addSection( sectionNumber, sectionName )

        markdownFiles = list(filter(lambda x: x.endswith('.md'), files ))
        pdfFiles = list(filter(lambda x: x.endswith('.pdf'), files))

        preparedFiles = list(filter(lambda x: "&" in x, pdfFiles ) )
        directFiles =   list(filter(lambda x: "%" in x, pdfFiles ))
        downloadFiles = list(filter(lambda x: "$" in x, pdfFiles ))

        otherFiles = list(set(pdfFiles) -set(preparedFiles) - set(directFiles) - set(downloadFiles)	)

        if otherFiles:
            log.warn(f'in directory {directory}...' )
            for o in otherFiles:
                log.warn(f'file not recognised {o}' )

        # log.debug(markdownFiles)
        # log.debug(pdfFiles)
        # log.debug(otherFiles)

        self.processMarkdown( sectionNumber, sectionName, directory, markdownFiles )
        self.processPreparedFiles( sectionNumber, sectionName, directory, preparedFiles )
        self.processDirectFiles( sectionNumber, sectionName, directory, directFiles )
        self.processDownloadFiles( sectionNumber, sectionName, directory, downloadFiles )

    def compile(self):
        _,directories,_  = next(os.walk(self.root))

        
        for directory in directories:  # Get top-level directories
            if '#' in directory:
                log.info(f'{directory} (directory/section)')
                _,_,files = next( os.walk(directory) )  # Get files in each
                self.processFiles(directory, files)
        self.createTOC()




