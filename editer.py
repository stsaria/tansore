import traceback, logging, csv
from etc import file_identification_rewriting

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s", filename="./tansore.log")
logger = logging.getLogger(__name__)

def edit(barcode : str, name : str, email : str):
    logger.info("CSV Edit")
    try:
        barcodes = []
        names = []
        emails = []
        with open("./barcodes/barcodes.csv", encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                barcodes.append(row[0])
                names.append(row[1])
                emails.append(row[2])
        num = None
        if not barcode in barcodes or not len(barcode) == 10 or not barcode.isdigit():
            logger.error("|Error : Unknow Barcode")
            return 2, ""
        for i in range(len(barcodes)):
            if barcodes[i] == barcode:
                num = i
        before_name = names[num]
        before_email = emails[num]
        after_name = name
        after_email = email
        if email == "" or "," in email or not len(email.split("/")) == email.count('@'):
            after_email = "email"
        if not before_email == "email" and after_email == "email":
            after_email = before_email
        if name == "" or "," in name:
            after_name = "name"
        if after_name == "name" and not after_email == "email":
            after_name = before_name
        if name == "" and email == "":
            after_email = "email"
            after_name = "name"
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