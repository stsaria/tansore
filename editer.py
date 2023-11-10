import traceback, logging, csv, os
from etc import file_identification_rewriting

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter("%(asctime)s@ %(message)s"))
os.makedirs('./log', exist_ok=True)

file_handler = logging.FileHandler("./log/tansore.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s '%(funcName)s'")
)

logging.basicConfig(level=logging.NOTSET, handlers=[stream_handler, file_handler])
logger = logging.getLogger(__name__)

def edit(barcode : str, name : str, email : str, new_barcode : bool):
    logger.info("CSV Edit")
    try:
        barcodes = []
        names = []
        emails = []
        with open("barcodes/barcodes.csv", encoding="utf-8") as f:
            text = f.read()
        with open(f"barcodes/barcodes.csv.backup", encoding="utf-8", mode="w") as f:
            f.write(text)
        with open("./barcodes/barcodes.csv", encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                barcodes.append(row[0])
                names.append(row[1])
                emails.append(row[2])
        num = None
        after_name = name
        after_email = email
        if barcode == "":
            logger.error("|Error : Input barcode is empty")
            return 2, ""
        if email == "" or "," in email or not len(email.split("/")) == email.count('@'):
            after_email = "email"
        if name == "" or "," in name:
            after_name = "name"
        if name == "" and email == "":
            after_email = "email"
            after_name = "name"
        if new_barcode:
            if_trailing_endline = None
            for line in open("barcodes/barcodes.csv", encoding="utf-8"):
                pass
            if line.endswith("\n"):
                if_trailing_endline = True
            else:
                if_trailing_endline = False
            with open("barcodes/barcodes.csv", encoding="utf-8", mode="a") as f:
                if not if_trailing_endline:
                    f.write("\n")
                f.write(barcode+","+after_name+","+after_email+"\n")
        else:
            if not barcode in barcodes or not len(barcode) == 10 or not barcode.isdigit():
                logger.error("|Error : Unknow Barcode")
                return 2, ""
            for i in range(len(barcodes)):
                if barcodes[i] == barcode:
                    num = i
            before_name = names[num]
            before_email = emails[num]
            if not before_email == "email" and after_email == "email":
                after_email = before_email
            if after_name == "name" and not after_email == "email":
                after_name = before_name
            file_identification_rewriting("./barcodes/barcodes.csv", barcode, barcode+","+after_name+","+after_email+"\n")
        logger.info("|Success")
        return 0, ""
    except:
        error = traceback.format_exc()
        logger.error("|Error : Unknow\n"+error)
        return 1, error

def backup_file(file_name : str):
    logger.info("Backup")
    try:
        with open(f"./barcodes/{file_name}", encoding="utf-8") as f:
            contents_now_file = f.read()
        with open(f"./barcodes/{file_name}.backup", encoding="utf-8") as f:
            contents_backup_file = f.read()
        with open(f"./barcodes/{file_name}", encoding="utf-8", mode='w') as f:
            f.write(contents_backup_file)
        with open(f"./barcodes/{file_name}.backup", encoding="utf-8", mode='w') as f:
            f.write(contents_now_file)
        logger.info("|Success")
        return 0
    except:
        error = traceback.format_exc()
        logger.info("|Error : Backup fail\n"+error)
        return 1

def direct_edit_file(file_name : str, after_text : str):
    try:
        with open(f"barcodes/{file_name}", encoding="utf-8") as f:
            text = f.read()
        with open(f"barcodes/{file_name}", encoding="utf-8", mode="w") as f:
            f.write(after_text)
        if not after_text == text:
            with open(f"barcodes/{file_name}.backup", encoding="utf-8", mode="w") as f:
                f.write(text)
        logger.info("Success")
        return 0
    except:
        error = traceback.format_exc()
        logger.error("|Error : Edit fail\n"+error)
        return 1