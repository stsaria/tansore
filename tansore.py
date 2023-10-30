import threading, platform, logging, time, sys, os
from etc import check_network

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s", filename="./tansore.log")
logger = logging.getLogger(__name__)

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
        if not "--install" in args:
            print(help)
            sys.exit(0)
    if "--install" in args:
        from install import install_tansore
        install_tansore()
    logger.info("System Name : "+platform.system())
    if "--no-check-system-name" in args:
        logger.info("| Pass")
    elif platform.system() in ["Windows", "Linux"]:
        logger.info("| OK")
    else:
        logger.info("| NG")
        sys.exit(1)
    logger.info("Python Ver : "+".".join(platform.python_version().split(".")[:2]))
    if "--no-check-python-ver" in args:
        logger.info("| Pass")
    elif int(platform.python_version().split(".")[:2][0]) == 3 and int(platform.python_version().split(".")[:2][1]) >= 6:
        logger.info("| OK")
    else:
        logger.info("| NG")
        sys.exit(1)
    logger.info("Network Check")
    if "--no-check-net" in args:
        period_stop = True
        logger.info("|Pass")
    elif not check_network():
        period_stop = True
        logger.info("|Error")
        sys.exit(2)
    else:
        period_stop = True
        logger.info("|Success")
    from gui import gui
    gui()

if __name__ == "__main__":
    main(sys.argv)
    logger.info("STOP!!")
