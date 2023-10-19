import sys
from gui import *
from install import *

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-install":
            install_tansore()
        else:
            print("I'm not sure about this argument.......")
    else:
        gui()
