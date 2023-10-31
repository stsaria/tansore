import configparser, traceback, datetime, shutil, zipfile, hashlib, logging, socket, os
from mail import send_file_gmail
from getter import get_personal_data

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter("%(asctime)s@ %(message)s"))
os.makedirs('./log', exist_ok=True)

file_handler = logging.FileHandler(
    f"./log/tansore.log"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s '%(funcName)s'")
)

logging.basicConfig(level=logging.NOTSET, handlers=[stream_handler, file_handler])
logger = logging.getLogger(__name__)

def replace_func(fname, replace_set):
    target, replace = replace_set
    with open(fname, 'r', encoding='utf-8') as f1:
        tmp_list =[]
        for row in f1:
            if row.find(target) != -1:
                tmp_list.append(replace)
            else:
                tmp_list.append(row)
    with open(fname, 'w', encoding='utf-8') as f2:
        for i in range(len(tmp_list)):
            f2.write(tmp_list[i])

def file_identification_rewriting(file_name, before, after):
    replace_setA = (before, after)
    replace_func(file_name, replace_setA)

def check_network(host = "google.com", port = 80):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return_code = sock.connect_ex((host, port))
        sock.close()
        if return_code == 0:
            return True
        else:
            return False
    except:
        return False

try:
    with open("./barcodes/setting.ini", encoding='utf-8') as f:
        text = f.read()
    if not "location" in text:
        file_identification_rewriting("./barcodes/setting.ini", "[etc]", "[etc]\nlocation = 未設定な施設\n")
    ini = configparser.ConfigParser()
    path = os.getcwd() + os.sep + 'barcodes/setting.ini'
    ini.read(path, 'UTF-8')
    password = ini["admin"]["password"]
    mail_address = ini["gmail"]["mail_address"]
    app_pass = ini["gmail"]["app_pass"]
    location = ini["etc"]["location"]
    title = [ini["title_setting"]["arriving"], ini["title_setting"]["gohome"]]
    text = [ini["text_setting"]["arriving"], ini["text_setting"]["gohome"]]
    etc = [int(ini["etc"]["send_csv_deadline_day"]), int(ini["etc"]["send_csv_deadline_time"]), int(ini["etc"]["arriving_deadline_time"]), int(ini["etc"]["arriving_isolation_period_min"])]
    if mail_address.count("@") == 1 or len(app_pass.replace(" ", "")) == 16:
        raise Exception
except:
    pass

def send_data(login : bool, dt_now = datetime.datetime.now()):
    logger.info("Send Data & LOG")
    try:
        os.makedirs("data-log", exist_ok=True)
        format_dt_now = dt_now.strftime('%Y/%m/%d %H:%M:%S')
        logger.info("Log")
        with open("./log/tansore.log", encoding="utf-8") as f:
            log_text = f.read()
        with open("./data-log/tansore.log", mode='w', encoding="utf-8") as f:
            f.write(log_text)
        with open("./log/tansore.log", mode="w", encoding="utf-8") as f:
            f.write("")
        logger.info("Attendance Data")
        personal_data = get_personal_data(csv_file = "./barcodes/barcodes.csv")
        files = os.listdir("barcodes")
        arriving_files = []
        for i in files:
            if ".txt" in i and i.replace(".txt", "").isdigit():
                arriving_files.append(i)
        for i in arriving_files:
            name = personal_data[i.replace(".txt", "")][0]
            with open("barcodes/"+i, encoding="utf-8") as f:
                text_list = f.readlines()
            text = "時間,種類\n"
            for j in text_list:
                text = text + j.replace(":", "年", 1).replace(":", "月", 1).replace(":", "日", 1).replace("/0", ",登校").replace("/1", ",下校")
            with open("./data-log/"+name+"-"+i.replace(".txt", ".csv"), mode='w', encoding="utf-8") as f:
                f.write(text)
            with open("./barcodes/old-"+format_dt_now.split(" ")[0].split("/")[0]+"-"+format_dt_now.split(" ")[0].split("/")[1]+"-"+i, mode='w', encoding="utf-8") as f:
                f.write("".join(text_list))
            with open("barcodes/"+i, mode="w", encoding="utf-8") as f:
                f.write("")
        zp = zipfile.ZipFile("data-log.zip", "w")
        for i in os.listdir("data-log"):
            zp.write("data-log/"+i)
        zp.close()

        send_file_gmail(mail_address, app_pass, [mail_address], "data-log", "Send Data & LOG\nTHIS IS IMPORTANT", ["data-log.zip"])
        
        shutil.rmtree("data-log")
        os.remove("data-log.zip")
        text_list = []
        if login == False:
            if os.path.isfile('./log/send-log.txt'):
                with open('./log/send-log.txt', mode='r', encoding="utf-8") as f:
                    text_list = f.readlines()
            with open('./log/send-log.txt', mode='a', encoding="utf-8") as f:
                if len(text_list) > 0:
                    f.write("\n"+format_dt_now.split(" ")[0])
                else:
                    f.write(format_dt_now.split(" ")[0])
        logger.info("|Success")
        return 0
    except:
        error = traceback.format_exc()
        logger.error("|Error : Unknow\n"+error)
        return 1

def setting_password(password : str):
    try:
        input_password = hashlib.sha256(password.encode()).hexdigest()
        file_identification_rewriting("./barcodes/setting.ini", "password", "password = "+input_password+"\n")
        return 0
    except:
        error = traceback.format_exc()
        print(error)
        return 1