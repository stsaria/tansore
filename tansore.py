import threading, platform, time, sys, os
from etc import check_network

period_stop = False

help = """Help
[args]
empty = Run Tansore(Want barcodes/ dir)
--install = Install Tansore(CUI)
--no-check-net = Disable Network Check(But if Network disconnect = email send result = Error)
--no-check-system-name = Disable System Name(e.g Windows) check(But if tansore want system != your system = Error)
--no-check-python-ver = Disable Python Ver(e.g 3.5) check(But if module want python ver > your python ver = Error)"""

def period_print():
    global period_stop
    while not period_stop:
        print(".", end="")
        time.sleep(0.5)
    period_stop = False

def main(args : list):
    global period_stop
    global help
    print("Tansore\nLICENCE : LGPL v3.0\nGithub : https://github.com/stsaria/tansore\n")
    if "--help" in args or not os.path.isdir("barcodes/"):
        print(help)
        sys.exit(0)
    print("System Name :", platform.system(),end="")
    if "--no-check-system-name" in args:
        print(" = Pass")
    elif platform.system() in ["Windows", "Linux"]:
        print(" = OK")
    else:
        print(" = NG")
        sys.exit(1)
    print("Python Ver :" , ".".join(platform.python_version().split(".")[:2]),end="")
    if "--no-check-python-ver" in args:
        print(" = Pass")
    elif int(platform.python_version().split(".")[:2][0]) == 3 and int(platform.python_version().split(".")[:2][1]) >= 6:
        print(" = OK")
    else:
        print(" = NG")
        sys.exit(1)
    period_print_thread = threading.Thread(target=period_print)
    print("\nNetwork ",end="")
    period_print_thread.start()
    if "--no-check-net" in args:
        period_stop = True
        print(" Pass")
    elif not check_network():
        period_stop = True
        print(" Error")
        sys.exit(2)
    else:
        period_stop = True
        print(" Success")
    del period_print_thread
    if "--install" in args:
        from install import install_tansore
        install_tansore()
    from gui import gui
    gui()

if __name__ == "__main__":
    main(sys.argv)
