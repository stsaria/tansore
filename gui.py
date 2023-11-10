import configparser, threading, traceback, platform, datetime, hashlib, tkinter, logging, time, os
import PySimpleGUI as sg
from editer import *
from attendance import *
from etc import *

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

logger.info("GUI Start")
for i in range(20):
    try:
        sg.theme("Kayak")
        root = tkinter.Tk()
        monitor_height, monitor_width = root.winfo_screenheight(), root.winfo_screenwidth()
        root.withdraw()
        layout_attendance = [
                [sg.Text("勤怠 - 出席・下校", font=("",15))],
                [sg.Text("バーコード:"), sg.Input(key="barcodeattendance")],
                [sg.Multiline(key="statusattendance", expand_x=True, expand_y=True,  pad=((0,0),(0,0)), disabled=True, default_text="バーコードを読み込んでください\n", autoscroll=True)]
                ]
        layout_csv_edit = [
                [sg.Text("内容変更", font=("",15)), sg.Text("注:・何も入力しない場合は空になります・BackUpファイルは一個しかありません\n・2回変えると一回目のデータは消えます・復元は直接編集のタブでできます\n・名前にnameと入力するのは避けてください")],
                [sg.Text("バーコード"), sg.InputText(key="barcodeedit")],
                [sg.Text("名前"), sg.InputText(key="name")],
                [sg.Text("Email('/'区切り)"), sg.InputText(key="email")],
                [sg.Checkbox("新たにバーコードを追加(既存のバーコードを追加する)", key="newbarcode")],
                [sg.Checkbox("名前をローマ字からひらがなに変換する(romkan)", key="ifromkan")],
                [sg.Multiline(key="statusedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, default_text="情報を書いてください\n", autoscroll=True)],
                [sg.Button("変更",key="csvedit")]
                ]
        layout_csv_view = [
                [sg.Text("CSV VIEW", font=("",15)), sg.Button("勤怠情報等情報送信",key="senddatalog"), sg.Text(key="statussenddatalog")],
                [sg.Text("空はいま登録されてないバーコードです")],
                [sg.Multiline(key="csv", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, autoscroll=True)]
                ]
        layout_setting = [
                [sg.Text("設定", font=("",15))],
                [sg.Text("_____________________________________________________________________________________________________________________")],
                [sg.Text("パスワード設定", font=("",13))],
                [sg.Text("パスワード再設定"), sg.Input(key="repassword"), sg.Button("設定", key="passwordsetting")],
                [sg.Text("_____________________________________________________________________________________________________________________")],
                [sg.Text(f"コンピューター情報\nOS:{platform.system()} {platform.release()}\nPython:{platform.python_version()}")],
                [sg.Text("_____________________________________________________________________________________________________________________")],
                [sg.Text("作成元 : Saria(st)\nライセンス : LGPL Licence v3.0(Githubにも記載)")],
                [sg.Text("_____________________________________________________________________________________________________________________")],
                [sg.Text(key="settingstatus")]
                ]
        layout_direct_edit_file = [
                [sg.Text("Direct Edit File", font=("",15)), sg.Text(key="statusdirectedit")],
                [sg.Text("警告：直接ファイルを書き換えることは推奨されていません")],
                [sg.Combo(["barcodes.csv", "setting.ini"], key="selectfile", default_value="ファイルを選択してください", size=26, enable_events=True, readonly=True)],
                [sg.Multiline(key="inputedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), autoscroll=True)],
                [sg.Button("書き換え",key="directedit"), sg.Button("再取得(巻き戻し)",key="regetfile"), sg.Button("復元",key="backup")]
                ]
        frame_login = [      
            [sg.Text("管理者パスワード"), sg.Input(key="password")],
            [sg.Button("ログイン", key="login"), sg.Button("ログアウト", key="logout"), sg.Button("終了(再起動)", visible=False, key="exit"), sg.Text(key="statuslogin")]
        ]
        layout_main = [
                [sg.Text("-Attendance System-", font=("",25), key="title"), sg.Text(key="time", font=("",17))],
                [sg.Frame("ログイン",frame_login)],
                [sg.TabGroup([[
                sg.Tab("勤怠", layout_attendance),
                sg.Tab("CSV編集", layout_csv_edit, visible=False, key="csveditab"),
                sg.Tab("CSV閲覧", layout_csv_view, visible=False, key="csvviewtab"),
                sg.Tab("直接編集", layout_direct_edit_file, visible=False, key="directeditfiletab"),
                sg.Tab("設定", layout_setting, visible=False, key="settingtab")
                ]], size=(monitor_width, monitor_height))]
                ]
        window = sg.Window("Yes Barcode System", layout_main, margins=(0,0), size=(monitor_width, monitor_height), resizable=True, finalize=True, no_titlebar=True, location=(0,0)).Finalize()
        window.Maximize()
        window["barcodeattendance"].set_focus()
        if platform.system() == "Windows":
            window["ifromkan"].update(visible=False)
        logger.info("|Success")
        break
    except:
        logger.error("|Error")
        error = traceback.format_exc()
        logger.error("This is Gui-error -----\n"+error+"-----------------------")
        time.sleep(6)

count = 1000

def countdown_quit(n = 8):
    global count
    time.sleep(2)
    for i in range(n):
        count = n-(i+1)
        text = "プログラム終了まで "+str(count)+"秒"
        window["statuslogin"].update(text)
        window["settingstatus"].update(text)
        window["statusedit"].update(text)
        window["statusdirectedit"].update(text)
        window["statusattendance"].update(text)
        time.sleep(1)

def gui():
    barcodes_txt_file_list = []
    global period_stop
    countdown_quit_target = threading.Thread(target=countdown_quit)
    try:
        logger.info("Search barcodes/*.txt")
        for file in os.listdir("./barcodes/"):
            base, ext = os.path.splitext(file)
            if ext == ".txt":
                barcodes_txt_file_list.append(file)
        logger.info("|length = "+str(len(barcodes_txt_file_list)))
    except Exception as e:
        logger.error("|Error\n"+str(e))
        return 3
    window["selectfile"].update(values = ["barcodes.csv", "setting.ini"] + barcodes_txt_file_list, value="ファイルを選択してください")
    try:
        logger.info("Read barcodes/setting.ini")
        with open("./barcodes/setting.ini", encoding="utf-8") as f:
            text = f.read()
        ini = configparser.ConfigParser()
        path = os.getcwd() + os.sep + "barcodes/setting.ini"
        ini.read(path, "UTF-8")
        mail_address = ini["gmail"]["mail_address"]
        app_pass = ini["gmail"]["app_pass"]
        password = ini["admin"]["password"]
        text = [ini["text_setting"]["arriving"], ini["text_setting"]["gohome"]]
        etc = [int(ini["etc"]["send_csv_deadline_day"]), int(ini["etc"]["send_csv_deadline_time"]), int(ini["etc"]["arriving_deadline_time"]), int(ini["etc"]["arriving_isolation_period_min"])]
        location = ini["etc"]["location"]
        if not mail_address.count("@") == 1 or not len(app_pass.replace(" ", "")) == 16:
            raise Exception
        logger.info("|Success")
    except Exception as e:
        logger.error("|Error\n"+str(e))
        return 4
    window["title"].update(location+" -Attendance System-")
    login = False
    while True:
        global count
        if count <= 0:
            break
        dt_now = datetime.datetime.now()
        format_dt_now = dt_now.strftime("%Y/%m/%d %H:%M:%S")
        final_send_csv_season = ["", "", ""]
        if os.path.isfile("./log/send-log.log"):
            f = open("./log/send-log.log", "r")
            alltxt = f.readlines()
            f.close()
            final_send_csv_season = alltxt[-1].strip().split("/")
        event, values = window.read(timeout=50)
        window["time"].update(format_dt_now)
        if event == sg.WIN_CLOSED or event == "exit":
            break
        elif " " in values["barcodeattendance"]:
            try:
                status = values["statusattendance"] + "\n"
                window["statusattendance"].update(status)
                result, error = attendance(values["barcodeattendance"].replace(" ", ""))
                if result == 0:
                    status = status + "勤怠しました\n"
                elif result == 1:
                    status = status + "原因不明なエラーが発生しました\nエラーを報告しました\nerror: "+error+"\n"
                elif result == 2:
                    status = status + "正しいバーコードを読み込んでください\n"
                elif result == 3:
                    status = status + "リストから名前が見つかりませんでした\n"
                elif result == 4:
                    status = status + f"{str(etc[3])}分の動作は許されません\n"
                elif result == 5:
                    status = status + "Emailの送信に失敗しました\n"
                window["statusattendance"].update(status)
            except:
                error = traceback.format_exc()
                logger.error("|Error : GUI Error \n"+error)
                window["statusattendance"].update(status + "GUIで原因不明なエラーが発生しました\nerror : "+error)
            window["statusattendance"].update(status + "\n\nバーコードを読み込んでください")
            window["barcodeattendance"].update("")
        elif event == "csvedit":
            status = values["statusedit"] + "\n"
            name = values["name"]
            if login == False:
                status = status + "管理者ではありません\n"
                window["statusedit"].update(status)
                logger.error("CSV Edit|Error : Now not admin")
                continue
            else:
                try:
                    if values["ifromkan"]:
                        import romkan
                        name = romkan.to_hiragana(name)
                    result, error = edit(values["barcodeedit"], name, values["email"], values["newbarcode"])
                    if result == 0:
                        status = status + "編集しました\nbarcodes/barcodes.csv.backupがバックアップファイルです"
                    elif result == 1:
                        status = status + "原因不明なエラーが発生しました\nエラーを報告しました\nerror: "+error+"\n"
                    elif result == 2:
                        status = status + "正しいバーコードを入力してください\n"
                    window["statusedit"].update(status)
                except ModuleNotFoundError:
                    error = traceback.format_exc()
                    logger.error("|Error : Module 'romkan' not found\n"+error)
                    window["statusedit"].update(status + "ローマ字変換モジュール(romkan)がありません"+error)
                except Exception:
                    error = traceback.format_exc()
                    logger.error("|Error : GUI Error\n"+error)
                    window["statusedit"].update(status + "GUIで原因不明なエラーが発生しました\nerror : "+error)
            window["statusedit"].update(status + "\n\n情報を書いてください")
            window["barcodeedit"].update("")
            window["name"].update("")
            window["email"].update("")
            with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                text_list = f.readlines()
            window["csv"].update("".join(text_list[1:]).replace(",name,email", ",空"))
            if values["selectfile"] == "barcodes.csv":
                window["inputedit"].update("".join(text_list))
        elif event == "senddatalog" or int(format_dt_now.split(" ")[0].split("/")[2]) >= etc[0] and int(format_dt_now.split(" ")[1].split(":")[0]) >= etc[1] and not [format_dt_now.split(" ")[0].split("/")[0], format_dt_now.split(" ")[0].split("/")[1]] == [final_send_csv_season[0], final_send_csv_season[1]]:
            if event == "senddatalog" and login == False:
                window["statussenddatalog"].update("管理者ではありません\n")
                logger.error("Send Data & LOG|Now not admin")
                continue
            try:
                result = send_data(login, dt_now=dt_now)
                if result == 0:
                    window["statussenddatalog"].update("送信しました")
                elif result == 1:
                    window["statussenddatalog"].update("原因不明なエラーが発生しました")
            except:
                error = traceback.format_exc()
                logger.error("|Error : GUI Error\n"+error)
                window["statussenddatalog"].update("GUIで原因不明なエラーが発生しました")
        elif event == "login":
            logger.info("User Login")
            if login == True:
                window["statuslogin"].update("すでにログインしています")
                logger.error("|Error : Already admin")
                continue
            input_password = hashlib.sha256(values["password"].encode()).hexdigest()
            if password == input_password:
                window["password"].update("")
                logger.info("|Success")
                window["statuslogin"].update("ログインしました")
                window["exit"].update(visible=True)
                window["csveditab"].update(visible=True)
                window["csvviewtab"].update(visible=True)
                window["settingtab"].update(visible=True)
                window["directeditfiletab"].update(visible=True)
                login = True
            else:
                window["statuslogin"].update("パスワードが違います")
                logger.error("|Not match Password Error")
                continue
            with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                text_list = f.readlines()
            window["csv"].update("".join(text_list[1:]).replace(",name,email", ",空"))
            if values["selectfile"] == "barcodes.csv":
                window["inputedit"].update("".join(text_list))
        elif event == "logout":
            logger.info("User Logout")
            if login != True:
                window["statuslogin"].update("ログインしていません")
                logger.info("|Error : Now not admin")
                continue
            login = False
            window["exit"].update(visible=False)
            window["csveditab"].update(visible=False)
            window["csvviewtab"].update(visible=False)
            window["settingtab"].update(visible=False)
            window["directeditfiletab"].update(visible=False)
            logger.info("|Success")
            window["statuslogin"].update("ログアウトしました")
            window["inputedit"].update("")
            window["csv"].update("")
        elif event == "passwordsetting":
            logger.info("New Password Setting")
            try:
                if login != True:
                    window["settingstatus"].update("管理者ではありません\n")
                    logger.error("|Error : Now not admin")
                    continue
                window["repassword"].update("")
                result = setting_password(values["repassword"])
                logger.info("|Success : Reboot...")
                window["settingstatus"].update("パスワードを変更しました 再起動しています\n")
                countdown_quit_target.start()
            except:
                error = traceback.format_exc()
                logger.error("|Error : Unknow\n"+error)
                window["settingstatus"].update("原因不明なエラーが発生しました\nerror : "+error+"\n")
        elif event == "selectfile":
            with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                text = f.read()
            window["inputedit"].update(text)
            logger.info("Select File|File : "+values["selectfile"])
        elif event == "directedit":
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                logger.error("Direct Edit|Error : Now not admin")
                continue
            try:
                if not os.path.isfile("barcodes/"+values["selectfile"]):
                    window["statusdirectedit"].update("選択したファイルがありません")
                    logger.error("Direct Edit|Error : Not select status")
                    continue
                result = direct_edit_file(values["selectfile"], values["inputedit"])
                if result == 0:
                    logger.info("|Reboot...")
                    window["statusdirectedit"].update("書き換えに成功しました\n再起動しています\n(一個前のバックアップはbarcodes/"+values["selectfile"]+".backupにあります)")
                    countdown_quit_target.start()
                elif result == 1:
                    window["statusdirectedit"].update("書き換えに失敗しました")
                if values["selectfile"] == "barcodes.csv":
                    window["csv"].update(values["inputedit"].replace(",name,email", ",空"))
            except:
                error = traceback.format_exc()
                logger.error("|Error : GUI Error\n"+error)
                window["statusdirectedit"].update("GUIで原因不明なエラーが発生しました")
        elif event == "backup":
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                logger.error("Backup|Error : Now not admin")
                continue
            try:
                if not os.path.isfile("barcodes/"+values["selectfile"]):
                    window["statusdirectedit"].update("選択したファイルがありません")
                    logger.error("Backup|Error : Not select status")
                    continue
                result = backup_file(values["selectfile"])
                if result == 0:
                    logger.info("Reboot...")
                    window["statusdirectedit"].update("復元に成功しました\n再起動しています\n(今のファイルはbarcodes/"+values["selectfile"]+".backupに変わりました)")
                    countdown_quit_target.start()
                elif result == 1:
                    window["statusdirectedit"].update("復元に失敗しました")
                with open(f"./barcodes/"+values["selectfile"], encoding="utf-8") as f:
                    text = f.read()
                window["inputedit"].update(text)
                if values["selectfile"] == "barcodes.csv":
                    window["csv"].update(text.replace(",name,email", ",空"))
            except:
                error = traceback.format_exc()
                logger.info("Backup - Error : GUI Error\n"+error)
                window["statusdirectedit"].update("GUIで原因不明なエラーが発生しました")
        elif event == "regetfile":
            logger.info("Reget File")
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                logger.error("|Error : Now not admin")
                continue
            try:
                if not os.path.isfile("barcodes/"+values["selectfile"]):
                    window["statusdirectedit"].update("選択したファイルがありません")
                    logger.error("| Error : Not select status")
                    continue
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                    text = f.read()
                window["inputedit"].update(text)
                logger.error("|Success")
                window["statusdirectedit"].update("ファイルを再取得しました")
            except:
                error = traceback.format_exc()
                logger.info("|Error : Backup fail\n"+error)
                window["statusdirectedit"].update("ファイルの再取得に失敗しました")
    return 0