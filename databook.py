import click
from os.path import dirname, realpath, join
import os
import compiler
import linker
import glob 
import sys
import logging as log


class DataBook():
    def __init__(self, root ):
        log.debug(f'Initializing with root: {root}')
        self.root     = root
        self.build    = join(root,'.build')
        self.buildRef = join(root,'.build-ref')
        self.output   = join(root,'output')
        log.debug(f'                     {self.build},')
        log.debug(f'                     {self.buildRef}')
        log.debug(f'                     {self.output}')

        if not os.path.exists(root):
            raise Exception(f"Top-level (root) directory {root} doesn't exist.")

        for d in [self.build, self.buildRef, self.output ]:
            if not os.path.exists(d):
                os.makedirs(d)

        clean = True
        if clean:
            for d in [self.build, self.buildRef, self.output ]:
                r = glob.glob(os.path.join( d, "*"))
                for i in r:
                    log.debug(f'removing {i}')
                    os.remove(i)			
        log.debug(f'Initialized')
        

    def compile(self):
        log.info(f'Compiling')
        c = compiler.Compiler(self.root, self.build, self.buildRef, self.output, True)
        c.compile()
        log.info("Compiled source files")

    def link(self):
        log.info(f'Linking')
        # Linker has a context manager, so use it like so...
        with linker.Linker(self.build, self.buildRef, self.output ) as l:
            authoredFiles = glob.glob(os.path.join(self.build,'*.pdf' ) )
            log.info(f'{self.build}, {authoredFiles}')
            l.linkAuthored( authoredFiles )
            log.info("Linked authored files")

            referenceFiles = glob.glob(os.path.join(self.buildRef,'*.pdf' ) )
            log.debug( referenceFiles )
            l.linkReferences( referenceFiles )
            log.info("Linked reference files")



@click.command()
@click.option('--root', prompt='top-level directory', help='root of document project')
def main(root):
    db = DataBook( root ) # root = dirname(dirname(realpath(__file__)))
    db.compile()
    db.link()


if __name__ == '__main__':
    log.basicConfig(stream=sys.stdout, level=log.DEBUG, format='%(levelname)8s: ''%(filename)12s: ''%(lineno)4d:\t''%(message)s')
    log.info('Databook generator')
    main()


