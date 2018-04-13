from logging import *

LONGFORMAT='%(levelname)8s: ''%(filename)-20s: ''%(lineno)4d:\t''%(message)s'
SHORTFORMAT='%(levelname)-8s: %(message)s'

# Root logger gets everything.  Handlers defined below will filter it out...
getLogger('').setLevel(DEBUG)

# set up logging to file
def toFile( filename ):
    filehandler = FileHandler(filename,mode='w')
    filehandler.setLevel(INFO)
    filehandler.setFormatter(Formatter(LONGFORMAT))
    getLogger('').addHandler(filehandler) 
    info('logging initialized')


# define a Handler to sys.stderr
console = StreamHandler()
console.setLevel(DEBUG)
console.setFormatter(Formatter(SHORTFORMAT))
getLogger('').addHandler(console)
