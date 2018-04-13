import glob
import os

import log

# def findSourceFile(self, otherFiles, baseName):
#     srcRegex = baseName+r"\.*"
#     # src = None
#     #log.debug('srcRegex for files:', otherFiles )
#     for file in otherFiles:
#         #log.debug("RE:",  srcRegex, file)
#         srcMatch = re.match( srcRegex, file )
#         if srcMatch:
#             return file

#     return None

# def checkTimes(self,  directory, src, tgt ):
#     srctime = os.path.getmtime(join(directory,src))
#     tgttime = os.path.getmtime(join(directory,tgt))
#     #log.debug(srctime, tgttime)

#     if srctime > tgttime:
#         log.debug( f'WARNING: {tgt} may be out of date' )

#     def regexList(self,  pattern, stringList):
#         for s in stringList:
#             match = re.match(pattern, s)
#             if match:
#                 return match
#         return None


# Find the dependency (if any) of the given filename
# and check it.


def check(directory, filename):
    root, ext = os.path.splitext(filename)
    fullname = os.path.join(directory, filename)
    files = glob.glob(os.path.join(directory, f"{root}.*"))
    files.remove(fullname)

    if not files:
        log.warn(f"No dependency found for {filename}")
        return

    if len(files) != 1:
        log.warn(f"Ambiguous dependency for {filename}")
        return

    srcTime = os.path.getmtime(files[0])
    tgtTime = os.path.getmtime(fullname)
    if tgtTime < srcTime:

        log.warn(f"Target file {filename} is out of date: {tgtTime} < {srcTime}")


# This is hokey.  TODO
if __name__ == "__main__":
    LONGFORMAT = "%(levelname)8s: " "%(filename)12s: " "%(lineno)4d:\t" "%(message)s"
    log.basicConfig(level=log.DEBUG, format=LONGFORMAT)

    one = "dependency_test.cad"
    two = "dependency_test.doc"
    three = "dependency_test.pdf"

    with open(one, "w") as f:
        f.write(f"testing {one}")
    log.info("<<<<  the following should warn")
    check(".", one)
    log.info(">>>>>>")

    with open(two, "w") as f:
        f.write(f"testing {two}")

    log.info("<<<<  the following should warn")
    check(".", one)
    log.info(">>>>>>")

    log.info("<<<<  the following should not warn")
    check(".", two)
    log.info(">>>>>>")

    with open(three, "w") as f:
        f.write(f"testing {three}")

    log.info("<<<<  the following should warn")
    check(".", three)
    log.info(">>>>>>")

    os.remove(one)
    os.remove(two)
    os.remove(three)
