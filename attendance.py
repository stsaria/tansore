import configparser, traceback, datetime, logging, os
from mail import send_html_gmail
from getter import get_personal_data
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

def which_arriving_gohome(barcode : str, dt = datetime.datetime.now(), arriving_deadline_time = 18, arriving_isolation_period_min = 10):
    """type : 0 = arriving, 1 = gohome"""
    format_dt_now = dt.strftime('%Y:%m:%d:%H:%M:%S')
    if int(format_dt_now.split(":")[3]) >= arriving_deadline_time:
        return 1, 0
    if os.path.isfile("./barcodes/"+barcode+".txt"):
        with open("./barcodes/"+barcode+".txt", 'r', encoding="utf-8") as f:
            lines = f.readlines()
            if not len(lines) <= 0:                
                line = lines[len(lines)-1]
                last_line = line.split("/")
                last_line_time = last_line[0].split(":")
                last_line_which_one = last_line[1]
                if last_line_time[:3] == format_dt_now.split(":")[:3]:
                    if last_line_time[3] == format_dt_now.split(":")[3] and (int(format_dt_now.split(":")[4]) - int(last_line_time[4])) <= arriving_isolation_period_min:
                        return None, 1
                    elif last_line_which_one == "0":
                        return 1, 0
                    elif int(last_line_time[3]) >= arriving_deadline_time:
                        return 0, 0
                    else:
                        return 0, 0
                else:
                    return 0, 0
            else:
                return 0, 0
    else:
        return 0, 0

def attendance(barcode : str):
    logger.info("Attendance")
    try:
        format_dt_now = datetime.datetime.now().strftime('%Y:%m:%d:%H:%M:%S')
        data = get_personal_data(csv_file = "./barcodes/barcodes.csv")
        to = []
        name = ""
        try:
            to = data[barcode][1].split("/")
            name = data[barcode][0]
            if name == "" or name == "name":
                logger.error("|Error : Not name in list")
                return 3, ""
        except:
            logger.error("|Error : Read Barcode is Unknow code")
            return 2, ""
        type, result = which_arriving_gohome(barcode, arriving_deadline_time = etc[2], arriving_isolation_period_min = etc[3], dt = datetime.datetime.now())
        if result == 1:
            logger.error("|Error : every "+str(etc[3])+" min Attendance not allowed")
            return 4, ""
        if len(to) == data[barcode][1].count('@'):
            html = """<!DOCTYPE html>
<html>
<head>
    <title>{0}</title>
</head>
<body style="display: inline-block; background-color: #d8d1b3; text-align: center; padding : 15px 30px 15px 30px; padding: 10px; margin-bottom: 10px; border: 1px solid #333333;">
    <h1 style="font-family:Courier;">Tansore -Attendance System-</h1>
    <h4>このメールは{1}から発信されています</h4>
    {2}
    <h4>このメールと同時に{1}にも<br/>勤怠データが保存されています</h4>
    <h4>このプログラム(PythonによるGUIなど)を書いてくれる人がいれば<br/>
    <a href="mailto:solothunder.autoer@gmail.com">solothunder.autoer@gmail.com</a>にご連絡ください</h4>
    <footer>
    <div style="font-size:12px;">
        <p>バグがありましたら<a href="mailto:solothunder.autoer@gmail.com">solothunder.autoer@gmail.com</a>にご連絡ください</p>
        <p>Saria(st) <a href="https://github.com/stsaria">Gtihub</a><br/>
        Discord : test222</p>
    </div>
    </footer>
</body>
</html>"""
            try:
                if type == 0:
                    send_html_gmail(mail_address, app_pass, to, title[0], html.format(title[0], location, text[0].replace("/name/", name)), cc=to)
                else:
                    send_html_gmail(mail_address, app_pass, to, title[1], html.format(title[1], location, text[1].replace("/name/", name)), cc=to)
            except:
                error = traceback.format_exc()
                logger.error("|Error : Send email\n"+error)
                return 5, error
        text_list = []
        if os.path.isfile("./barcodes/"+barcode.replace(" ", "")+".txt"):
            with open("./barcodes/"+barcode.replace(" ", "")+".txt", mode='r', encoding="utf-8") as f:
                text_list = f.readlines()
        with open("./barcodes/"+barcode.replace(" ", "")+".txt", mode='a', encoding="utf-8") as f:
            if len(text_list) > 0:
                f.write(f'\n{format_dt_now}/{str(type)}')
            else:
                f.write(f'{format_dt_now}/{str(type)}')
        logger.info("|Success")
        return 0, ""
    except:
        error = traceback.format_exc()
        logger.error("|Error : Unknow\n"+error)
        return 1, error