import sys
import os

# position of the script -------------------------------------------------------
path_this = os.path.realpath(__file__)
path_array = path_this.split("/")
relative_path = "/".join(path_array[0:-1])

# add /bin to the path ---------------------------------------------------------
try:
    if os.path.isdir(relative_path):
        sys.path.insert(0, relative_path)
    else:
        sys.stderr.write("[E::main] Error: "+relative_path+" directory is missing.\n")
        sys.exit(1)
except:
    sys.stderr.write("[E::main] Error: "+relative_path+" directory is missing.\n")
    sys.exit(1)

try:
    import map_genes_to_mOTUs as map_motu
except:
    sys.stderr.write("[E::main] Error: fail to load the script: "+relative_path+"/map_genes_to_mOTUs.py\n")
    sys.exit(1)

try:
    import runBWA as runbwa
except ImportError:
    sys.stderr.write("[E::main] Error: fail to load the script: "+relative_path+"/runBWA.py\n")
    sys.exit(1)



def map(args):
    print("as")
    return 0

def index(args):
    return 0

def merge(args):
    return 0
