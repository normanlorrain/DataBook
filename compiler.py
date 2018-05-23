import datetime
import glob
import os
import os.path
import re
import shutil
import subprocess
import tempfile
from os.path import dirname, join, realpath

from util.config import config
import toc
import dependency
from util import log
import pandoc
import pdf


class Compiler:

    def __init__(self):
        self.contents = toc.Contents()

    def compileMarkdown(self, directory, src, tgt, coverPage=False):
        log.debug(f"compileMarkdown( {directory}, {src}, {tgt}, {coverPage})")
        src = join(config.root, directory, src)
        tgt = join(config.build, tgt)
        pandoc.run(src, tgt, coverPage)

    def getSectionNumber(self, path):
        # log.debug('getSectionNumber: ', path)
        match = re.match(r".*?#(\d+).*", path)
        if match:
            return int(match.group(1))

        else:
            return 0

    def getSectionName(self, path):
        # log.debug('getSectionName: ', path)
        match = re.match(r".*?#(\d+)(.*)", path)
        if match:
            # log.debug(match.groups())
            name = match.group(2).strip()
            # log.debug('name:',name)
            return name

        else:
            raise Exception("can't get name")

    def createTOC(self):
        filename = join(config.build, ".toc.md")
        log.debug(f'createTOC: opening {filename}')
        with open(filename, "w") as f:
            f.write(toc.header)
            for line in self.contents.markdownLines():
                f.write(line)
            f.write("\n\n")
        self.compileMarkdown(
            config.build, ".toc.md", "00-01 [Intro] [Table of Contents].pdf"
        )

    def globAndMatch(self, globPattern, rePattern ):
        fileList = glob.glob(globPattern)
        for singleFile in fileList:
            match = re.match(rePattern, singleFile )
            if match:
                subSectionNumber = int(match.group(1))
                subSectionName = match.group(2).strip()
                yield (singleFile, subSectionNumber, subSectionName)
            else:
                log.warn(f"Filename is in wrong format: {singleFile} ")
            


    def processMarkdown(self, sectionNumber, sectionName, directory ):
        os.chdir(directory)
        for markdownFile, subSectionNumber, subsectionName in self.globAndMatch("*.md",r"#(\d+)(.*?)\.md") :
            log.info(f"    {markdownFile} (Markdown file)")
            self.compileMarkdown(
                directory,
                markdownFile,
                f"{sectionNumber:02}-{subSectionNumber:02} [{sectionName}] [{subsectionName}].pdf",
                coverPage = (sectionNumber == 0) )
            self.contents.addSubSection(sectionNumber, subSectionNumber, subsectionName)


    def processPreparedFiles( self, sectionNumber, sectionName, directory ):
        os.chdir(directory)
        for filename, subSectionNumber, subsectionName in self.globAndMatch("*&*.pdf", r"#(\d+)\&(.*?)\.pdf") :
            log.info(f"    {filename} (prepared PDF file)")
            src = join(directory, filename)
            dst = join(
                config.build,
                f"{sectionNumber:02}-{subSectionNumber:02} [{sectionName}] [{subsectionName}].pdf" )
            shutil.copy(src, dst)
            self.contents.addSubSection(sectionNumber, subSectionNumber, subsectionName)
            dependency.check(directory, filename)

    def processDirectFiles(self, sectionNumber, sectionName, directory):
        os.chdir(directory)
        for filename, subSectionNumber, subsectionName in self.globAndMatch("*%*.pdf", r"#(\d+)\%(.*?)\.pdf") :
            log.info(f"    {filename} (directly edited PDF)")
            src = join(directory, filename)
            dst = join(
                config.build,
                f"{sectionNumber:02}-{subSectionNumber:02} [{sectionName}] [{subsectionName}].pdf",
            )
            shutil.copy(src, dst)
            self.contents.addSubSection(sectionNumber, subSectionNumber, subsectionName)

    def getReferenceDirectories( self, directory ):
        directoryList = [directory]

        for i in ['References', 'references', 'refs', 'ref' ]:
            testDir = os.path.join(directory, i)
            if os.path.isdir(testDir):
                directoryList.append(testDir)
            
        for d in directoryList:
            yield d
            
            
    def processReferenceFiles( self, sectionNumber, sectionName, topDirectory ):
        for directory in self.getReferenceDirectories(topDirectory):
            os.chdir(directory)
            for filename, documentNumber, documentName in self.globAndMatch("*$*.pdf", r"#(\d+)\$(.*?)\.pdf") :
                log.info(f"    {filename} (reference document/attachment)")
                watermarkText = f"REFERENCE DOCUMENT:  {sectionNumber}.{documentNumber} {sectionName} - {documentName}                  {config.title}, {config.datestamp} "
                watermarkPdf = os.path.join(tempfile.gettempdir(), "~databook_temp.pdf")
                pdf.generateMultipageWatermarkFile(
                    watermarkPdf, watermarkText, os.path.join(directory, filename)
                )

                # src = join(directory,filename)
                dst = join(
                    config.buildRef,
                    f"{sectionNumber:02}-{documentNumber:02} {sectionName}-{documentName}.pdf",
                )
                # shutil.copy(src, dst)
                self.contents.addSubSection(
                    sectionNumber, documentNumber, documentName + " (Attachment)"
                )

                cmd = f'pdftk "{join(directory,filename)}" multistamp "{watermarkPdf}" output "{dst}"'
                log.debug(cmd)
                try:
                    subprocess.run(cmd, check=True)
                except Exception as e:
                    log.exception(e)
                    raise

    def processSection(self, directory, section, parentSection=None):
        log.debug(f"processSection({directory}, {section}, {parentSection})")

        sectionNumber = self.getSectionNumber(section)
        sectionName = self.getSectionName(section)

        log.debug(f'Section Number: {sectionNumber}')
        log.debug(f'Section Name: {sectionName}')

        self.contents.addSection(sectionNumber, sectionName)
        
        subdir = os.path.join(directory, section)
        self.processMarkdown(sectionNumber, sectionName, subdir )
        self.processPreparedFiles(sectionNumber, sectionName, subdir )
        self.processDirectFiles(sectionNumber, sectionName, subdir )
        self.processReferenceFiles(sectionNumber, sectionName, subdir )
      
    def compile(self):
        _, directories, _ = next(os.walk(config.root))
        # sections = list( filter(lambda x: '#' in x, directories) )
        sections = [ x for x in directories if x.startswith('#') ]

        for section in sections:
            log.info(f"Top-level section: {section}")
            self.processSection( config.root, section)
        self.createTOC()
