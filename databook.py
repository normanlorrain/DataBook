import argparse
import compiler
import glob
import logging as log
import os
import sys
from os.path import dirname, join, realpath

import linker
import config


class DataBook():
    def __init__(self ):
        if not os.path.exists(config.root):
            raise Exception(f"Top-level (root) directory {self.root} doesn't exist.")

        for d in [config.build, config.buildRef ]:
            if not os.path.exists(d):
                os.makedirs(d)

        clean = True
        if clean:
            for d in [config.build, config.buildRef]:
                r = glob.glob(os.path.join( d, "*"))
                for i in r:
                    log.debug(f'removing {i}')
                    os.remove(i)			

        

    def compile(self):
        log.info(f'Compiling')
        c = compiler.Compiler( )
        c.compile()
        log.info( "Compiled source files" )

    def link(self):
        log.info(f'Linking')
        # Linker has a context manager, so use it like so...
        l =  linker.Linker( )
        authoredFiles = glob.glob(os.path.join(config.build,'*.pdf' ) )
        log.debug(f'{config.build}, {authoredFiles}')
        l.linkAuthored( authoredFiles )
        log.info("Linked authored files")

        referenceFiles = glob.glob(os.path.join(config.buildRef,'*.pdf' ) )
        log.debug( referenceFiles )
        l.linkReferences( referenceFiles )
        log.info("Linked reference files")



def main():
    config.initialize()
    db = DataBook() 
    db.compile()
    db.link()


if __name__ == '__main__':
    # set up logging to file - see previous section for more details
    LONGFORMAT='%(levelname)8s: ''%(filename)12s: ''%(lineno)4d:\t''%(message)s'
    SHORTFORMAT='%(levelname)-8s: %(message)s'
    log.basicConfig(level=log.DEBUG,
                        format=LONGFORMAT,
                        filename='databook.log',
                        filemode='w')
    
    filehandler = log.FileHandler('databook.log')
    filehandler.setLevel(log.WARNING)
    filehandler.setFormatter(log.Formatter(LONGFORMAT))
    log.getLogger('').addHandler(filehandler) 

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = log.StreamHandler()
    console.setLevel(log.INFO)
    console.setFormatter(log.Formatter(SHORTFORMAT))
    # add the handler to the root logger
    log.getLogger('').addHandler(console)

    log.info('Databook generator')

    main()
