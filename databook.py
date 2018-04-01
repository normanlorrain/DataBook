from os.path import dirname, realpath, join
import os
import compiler
import linker
import glob 
import sys
import logging as log
import argparse


class DataBook():
    def __init__(self, args ):
        log.debug(f'Initializing with root: {args.root}')
        self.root     = args.root
        self.build    = join(self.root,'.build')
        self.buildRef = join(self.root,'.build-ref')
        self.output   = join(self.root, args.output)
        log.debug(f'                     {self.build},')
        log.debug(f'                     {self.buildRef}')
        log.debug(f'                     {self.output}')

        if not os.path.exists(self.root):
            raise Exception(f"Top-level (root) directory {self.root} doesn't exist.")

        for d in [self.build, self.buildRef ]:
            if not os.path.exists(d):
                os.makedirs(d)

        clean = True
        if clean:
            for d in [self.build, self.buildRef]:
                r = glob.glob(os.path.join( d, "*"))
                for i in r:
                    log.debug(f'removing {i}')
                    os.remove(i)			

        os.chdir(self.root)
        self.loadConfiguration()
        log.debug(f'Initialized')

    def loadConfiguration(self):
        configName = os.path.join( self.root, 'configuration.json' )
        import json

        with open(configName) as json_data:
            self.config = json.load(json_data)

            log.debug(self.config)

    def compile(self):
        log.info(f'Compiling')
        c = compiler.Compiler( self.root, self.build, self.buildRef, self.config['title'], True )
        c.compile()
        log.info( "Compiled source files" )

    def link(self):
        log.info(f'Linking')
        # Linker has a context manager, so use it like so...
        with linker.Linker(self.build, self.buildRef, self.config['title'], self.output ) as l:
            authoredFiles = glob.glob(os.path.join(self.build,'*.pdf' ) )
            log.debug(f'{self.build}, {authoredFiles}')
            l.linkAuthored( authoredFiles )
            log.info("Linked authored files")

            referenceFiles = glob.glob(os.path.join(self.buildRef,'*.pdf' ) )
            log.debug( referenceFiles )
            l.linkReferences( referenceFiles )
            log.info("Linked reference files")



def main(args):
    db = DataBook( args ) # root = dirname(dirname(realpath(__file__)))
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

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = log.StreamHandler()
    console.setLevel(log.INFO)
    console.setFormatter(log.Formatter(SHORTFORMAT))
    # add the handler to the root logger
    log.getLogger('').addHandler(console)


    parser = argparse.ArgumentParser(description='Generate a "DataBook". See https://github.com/normanlorrain/DataBook.')
    parser.add_argument('root', help='root of document project')
    parser.add_argument('output', help='destination filename')
    args = parser.parse_args()

    log.debug(f'arguments: {args}')


    log.info('Databook generator')
    main(args)


