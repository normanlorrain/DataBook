import argparse
import subprocess
from os.path import join
import config 
import logging as log


# Pandoc offers following PDF support:
#     pdflatex   lualatex   xelatex :   all the same.  boring old LateX, but lots of flexibility.  See metadata.yaml.
#     wkhtmltopdf:  ugly layout
#     weasyprint: won't install on my python
#     prince: works, but has small icon on first page.  Won't to page breaks.
#     context: broken
#     pdfroff: not available on Windows

def run(src,tgt, coverPage= False):
    #metadata = join(config.root, 'metadata.yaml' )
    cmd = ['pandoc', src ]

    if coverPage: 
        cmd.append(  f'--metadata=title:"{config.title}"'    )
        cmd.append(  f'--metadata=author:"{config.author}"'  )
        cmd.append(  f'--metadata=date:"{config.datestamp}"' )

    cmd.extend( ['--pdf-engine=xelatex',
    f'--template={config.template}', 
        '-o',
        tgt] )

    #cmd=['ls', '-l']
    log.info(cmd)
    try:
        subprocess.run(cmd, shell=True, check = True )
    except subprocess.CalledProcessError as e:
        log.error( e.cmd )
        log.error( e.returncode )
        log.error( e.output) 
        log.error( e.stderr) 
        raise


if __name__ == '__main__':
    run()