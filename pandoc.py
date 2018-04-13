import glob
import os
import shutil
import subprocess

from config import config
import log

# Pandoc offers following PDF support:
#     pdflatex   lualatex   xelatex: preferring the later; it's more capable.
#     wkhtmltopdf:  ugly layout
#     weasyprint: won't install on my python
#     prince: works, but has small icon on first page.  Won't to page breaks.
#     context: broken
#     pdfroff: not available on Windows


def run(src, tgt, coverPage=False):
    oldDir = os.getcwd()
    srcDir = os.path.dirname(src)
    srcFile = os.path.basename(src)

    # prior runs of pdflatex, etc. will leave trash behind if they fail.
    for tex2pdf in glob.glob(os.path.join(srcDir, "tex2pdf.*")):
        log.warn(f"removing old tex2pdf directory: {tex2pdf}")
        shutil.rmtree(tex2pdf)

    cmd = ["pandoc", srcFile]

    if coverPage:
        cmd.append(f'--metadata=title:"{config.title}"')
        cmd.append(f'--metadata=author:"{config.author}"')
        cmd.append(f'--metadata=date:"{config.datestamp}"')

    cmd.extend(["--pdf-engine=xelatex", f"--template={config.template}", "-o", tgt])

    log.info(cmd)
    try:
        os.chdir(srcDir)
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        log.error(e.cmd)
        log.error(e.returncode)
        log.error(e.output)
        log.error(e.stderr)
        raise

    finally:
        os.chdir(oldDir)


