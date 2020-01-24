from logging import *

LONGFORMAT='%(levelname)8s: ''%(filename)-20s: ''%(lineno)4d:\t''%(message)s'
SHORTFORMAT='%(levelname)-8s: %(message)s'

# Root logger gets everything.  Handlers defined below will filter it out...
ROOTLOGGER = getLogger('')
ROOTLOGGER.setLevel(DEBUG)

# define a Handler to sys.stderr (on by default)
console = StreamHandler()
console.setLevel(DEBUG)
console.setFormatter(Formatter(SHORTFORMAT))
ROOTLOGGER.addHandler(console)

# Set up logging to file (optional).
def toFile( filename ):
    filehandler = FileHandler(filename,mode='w')
    filehandler.setLevel(INFO)
    filehandler.setFormatter(Formatter(LONGFORMAT))
    ROOTLOGGER.addHandler(filehandler) 
    info('logging initialized')


