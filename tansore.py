import threading, time, sys
from etc import check_network

period_stop = False

def period_print():
    global period_stop
    while not period_stop:
        print(".", end="")
        time.sleep(0.5)
    period_stop = False

period_print_thread = threading.Thread(target=period_print)
print("Network ",end="")
period_print_thread.start()
if not check_network():
    period_stop = True
    print(" Error")
    sys.exit(2)
else:
    period_stop = True
    print(" Success")
del period_print_thread

if __name__ == "__main__":
    period_print_thread = threading.Thread(target=period_print)
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-install":
            from install import *
            install_tansore()
        else:
            print("I'm not sure about this argument.......")
    else:
        from gui import gui
        gui()
