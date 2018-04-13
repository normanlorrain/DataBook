from logging import *

# set up logging to file - see previous section for more details
LONGFORMAT='%(levelname)8s: ''%(filename)-20s: ''%(lineno)4d:\t''%(message)s'
SHORTFORMAT='%(levelname)-8s: %(message)s'

# Root logger gets everything.  Handlers defined below will filter it out...

getLogger('').setLevel(DEBUG)

def toFile( filename ):
    filehandler = FileHandler(filename,mode='w')
    filehandler.setLevel(INFO)
    filehandler.setFormatter(Formatter(LONGFORMAT))
    getLogger('').addHandler(filehandler) 
    info('logging initialized')


# define a Handler which writes INFO messages or higher to the sys.stderr
console = StreamHandler()
console.setLevel(DEBUG)
console.setFormatter(Formatter(SHORTFORMAT))
# add the handler to the root logger
getLogger('').addHandler(console)
