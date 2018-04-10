#
# Manages a list of sections and subsections (and in the future, may be sub-sub...etc.)
# The goal is to generate the TOC page.compile
#

import logging as log
import os
import subprocess
from os.path import dirname, join, realpath

import pandoc

header = r"""
\begin{center} 

\huge Contents 

\end{center} 


"""
class Section:
    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.subsections = dict()

class Contents:
    def __init__(self):
        self.sections = dict()

    def addSection(self, sectionNumber, title ):
        if sectionNumber == 0:
            log.debug(f'skipping section 0 (cover page)')
            return

        self.sections[sectionNumber] = Section( sectionNumber, title ) 

    def addSubSection(self, section, number, title):
        if section == 0:
            log.debug(f'skipping section 0 (cover page)')
            return
        
        try:
            self.sections[section].subsections[number] = Section( number, title )
        except:
            log.error(f'Section {section} does not exist')
            raise

    def __iter__(self):
        for section in sorted(self.sections.keys()):
            for subsection in sorted(self.sections[section].subsections.keys()):
                yield section, subsection, self.sections[section].subsections[subsection].name

    def markdownLines(self):
        for section in sorted(self.sections.keys()):
            yield f'\n**{self.sections[section].number} {self.sections[section].name}**\n'
            for subsection in sorted(self.sections[section].subsections.keys()):
                yield f'\n\\quad{self.sections[section].subsections[subsection].number} {self.sections[section].subsections[subsection].name} \n'


def _compileMarkdown(directory, src,tgt):
    src = join(directory, src)
    tgt = join(directory, tgt)
    pandoc.run(src,tgt)

    

def test(directory):
    os.chdir(directory)
    log.info(directory)
    contents = Contents()
    contents.addSection(0, "Cars")
    contents.addSubSection(0,1,"Ford")
    contents.addSection(1, "Computers")
    contents.addSubSection(1,1,"Dell")
    contents.addSubSection(1,2,"IBM")
    for line in contents.markdownLines():
        print(line)

    markdownFile = ".test.md"
   
    log.debug(f'opening {directory} {markdownFile}')
    with open(join( directory, markdownFile ), 'w') as f:
        f.write(header)
        for line in contents.markdownLines():
            f.write(line)
        f.write("\n\n")

    _compileMarkdown( directory, 
                    markdownFile, 
                    ".test_toc.pdf" )


if __name__ == '__main__':
    import sys
    log.basicConfig(stream=sys.stdout, level=log.DEBUG, format='%(levelname)8s: ''%(filename)12s: ''%(lineno)4d:\t''%(message)s')
    test( dirname(dirname(realpath(__file__))) )
