import configparser, platform, tkinter, traceback, datetime, smtplib, shutil, hashlib, zipfile, csv, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
import PySimpleGUI as sg

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
except:
    print("error:ini file read")

while True:
    try:
        root = tkinter.Tk()

        monitor_height, monitor_width = root.winfo_screenheight(), root.winfo_screenwidth()
        root.withdraw()

        sg.theme("SystemDefault1")
        layout_attendance = [
                [sg.Text("Tansore -Attendance System-", font=('',15))],
                [sg.Text("バーコード:"), sg.Input(key="barcodeattendance")],
                [sg.Multiline(key="statusattendance", expand_x=True, expand_y=True,  pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="バーコードを読み込んでください\n", autoscroll=True)]
                ]
        layout_csv_edit = [
                [sg.Text('内容変更', font=('',15))],
                [sg.Text('バーコード'), sg.InputText(key='barcodeedit')],
                [sg.Text('名前'), sg.InputText(key='name')],
                [sg.Text('Email("/"区切り)'), sg.InputText(key='email')],
                [sg.Multiline(key="statusedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="情報を書いてください\n", autoscroll=True)],
                [sg.Button('変更',key='edit')]
                ]
        layout_csv_view = [
                [sg.Text('CSV VIEW', font=('',15)), sg.Button('勤怠情報送信',key='sendcsv'), sg.Text(key="statussendcsv")],
                [sg.Text('空はいま登録されてないバーコードです')],
                [sg.Multiline(key="csv", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, font=('Arial',15), autoscroll=True)]
                ]
        layout_setting = [
                [sg.Text('設定', font=('',15))],
                [sg.Text('_____________________________________________________________________________________________________________________')],
                [sg.Text('パスワード設定', font=('',13))],
                [sg.Text('パスワード再設定'), sg.Input(key="repassword"), sg.Button("設定", key="passwordsetting")],
                [sg.Text('_____________________________________________________________________________________________________________________')],
                [sg.Text(f"コンピューター情報\nOS:{platform.system()} {platform.release()}\nPython:{platform.python_version()}")],
                [sg.Text('_____________________________________________________________________________________________________________________')],
                [sg.Text('作成者 : stsaria\nライセンス : LGPL Licence')],
                [sg.Text('_____________________________________________________________________________________________________________________')],
                [sg.Text(key="settingstatus")]
                ]
        layout_direct_edit_file = [
                [sg.Text('Direct Edit File', font=('',15)), sg.Text(key="statusdirectedit")],
                [sg.Text('警告：直接ファイルを書き換えることは推奨されていません , 出席履歴ファイルは書き換えれません')],
                [sg.Combo(['barcodes.csv', 'setting.ini'], key='selectfile', default_value="ファイルを選択してください", enable_events=True, readonly=True)],
                [sg.Multiline(key="inputedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), font=('',15), autoscroll=True)],
                [sg.Button('書き換え',key='directedit'), sg.Button('再取得(巻き戻し)',key='regetfile')]
                ]
        layout_main = [
                [sg.Text("管理者パスワード"), sg.Input(key="password"), sg.Text(key="statuslogin")],
                [sg.Button("ログイン", key="login"), sg.Button("ログアウト", key="logout"), sg.Button("終了(再起動)", key="exit"), sg.Text(key="time", font=('Arial',15))],
                [sg.TabGroup([[
                sg.Tab("勤怠", layout_attendance),
                sg.Tab("CSV編集", layout_csv_edit, visible=False, key='editab'),
                sg.Tab("CSV閲覧", layout_csv_view, visible=False, key='csvviewtab'),
                sg.Tab("直接編集", layout_direct_edit_file, visible=False, key='directeditfiletab'),
                sg.Tab("設定", layout_setting, visible=False, key='settingtab')
                ]], size=(monitor_width, monitor_height))]
                ]

        window = sg.Window("Yes Barcode System", layout_main, margins=(0,0), size=(monitor_width, monitor_height), resizable=True, finalize=True, no_titlebar=True, location=(0,0)).Finalize()
        window.Maximize()
        window["barcodeattendance"].set_focus()
        break
    except:
        error = traceback.format_exc()
        print("This is Gui-error -----\n"+error+"-----------------------")
        continue

def get_personal_data(csv_file : str):
    data = {}
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            data[row[0]] = [row[1], row[2]]
    return data

def send_gmail(mail_address : str, app_pass : str, to : list, title : str, html : str):
    for i in to:
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(mail_address, app_pass)
        msg = MIMEText(html, "html")
        msg['Subject'] = title
        msg['From'] = mail_address
        msg['To'] = i
        msg['Date'] = formatdate()

        smtpobj.sendmail(mail_address, i, msg.as_string())
        smtpobj.close()

def sendgmailfile(mail_address : str, app_pass : str, to : list, title : str, text : str, file : list):
    for i in to:
        _msg = MIMEMultipart()
        _msg['From'] = mail_address
        _msg['To'] = i
        _msg['Subject'] = title
        _msg['Date'] = formatdate(timeval=None, localtime=True)
        _msg.attach(MIMEText(text, "plain"))
        for filename in file:
            with open(filename, 'rb') as _f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(_f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= {}'.format(filename))
            _msg.attach(part)
        context = ssl.create_default_context()
        _smtp = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465, timeout=10, context=context)
        _smtp.login(user=mail_address, password=app_pass)
        _smtp.sendmail(mail_address, i, _msg.as_string())
        _smtp.close()

def which_arriving_gohome(barcode : str, dt = datetime.datetime.now(), arriving_deadline_time = 18, arriving_isolation_period_min = 10):
    """0 = arriving, 1 = gohome"""
    type = None
    format_dt_now = dt.strftime('%Y:%m:%d:%H:%M:%S')
    if int(format_dt_now.split(":")[3]) >= arriving_deadline_time:
        return 1, 0
    if os.path.isfile("./barcodes/"+barcode+".txt"):
        with open("./barcodes/"+barcode+".txt", 'r', encoding="utf-8") as f:
            for line in f:  pass
            last_line = line.split("/")
            last_line_time = last_line[0].split(":")
            last_line_which_one = last_line[1]
            if last_line_time[:3] == format_dt_now.split(":")[:3]:
                if last_line_time[3] == format_dt_now.split(":")[3] and (int(format_dt_now.split(":")[4]) - int(last_line_time[4])) <= arriving_isolation_period_min:
                    return None, 1
                elif last_line_which_one == "0":
                    type = 1
                elif int(last_line_time[3]) >= arriving_deadline_time:
                    type = 0
                else:
                    type = 0
            else:
                type = 0
    else:
        type = 0
    return type, 0

def attendance(barcode : str):
    try:
        format_dt_now = datetime.datetime.now().strftime('%Y:%m:%d:%H:%M:%S')
        data = get_personal_data(csv_file = "./barcodes/barcodes.csv")
        to = ""
        name = ""
        try:
            to = data[barcode][1].split("/")
            name = data[barcode][0]
            if name == "" or name == "name":
                return 3, ""
        except:
            error = traceback.format_exc()
            print(error)
            return 2, error
        type, result = which_arriving_gohome(barcode, arriving_deadline_time = etc[2], arriving_isolation_period_min = etc[3])
        if result == 1:
            return 4, ""
        if len(to) == data[barcode][1].count('@'):
            html = """<!DOCTYPE html>
<html>
<head>
    <title>{0}</title>
</head>
<body style="background-color: #f2f1ed; text-align: center;">
    <h1 style="font-family:Courier;">Tansore -Attendance System-</h1>
    <div style="display:inline-block; background:#fcfcff; padding : 15px 30px 15px 30px;">
        <h4>このメールは{1}から発信されています</h4>
        <div style="padding: 10px; background-color: #f2f1ed; display:inline-block;">
            {2}
        </div>
        <h4>このメールと同時に{1}にも<br/>勤怠データが保存されています</h4>
    </div>
    <footer>
    <div style="font-size:12px;">
        <p>バグがありましたら<a href="mailto:solothunder.autoer@gmail.com">solothunder.autoer@gmail.com</a>にご連絡ください</p>
        <p>Saria(st) <a href="https://github.com/stsaria">Gtihub</a><br/>
        Discord : test222</p>
    </div>
    </footer>
</body>
</html>"""
            if type == 0:
                send_gmail(mail_address, app_pass, to, title[0], html.format(title[0], location, text[0].replace("/name/", name)))
            else:
                send_gmail(mail_address, app_pass, to, title[1], html.format(title[1], location, text[1].replace("/name/", name)))
        with open("./barcodes/"+barcode.replace(" ", "")+".txt", mode='a', encoding="utf-8") as f:
            f.write(f'{format_dt_now}/{str(type)}\n')
        return 0, ""
    except:
        error = traceback.format_exc()
        print(error)
        return 1, error

def edit(barcode : str, name : str, email : str):
    try:
        barcodes = []
        with open("./barcodes/barcodes.csv", encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                barcodes.append(row[0])
        if not barcode in barcodes or not len(barcode) == 10 or not barcode.isdigit():
            return 2, ""
        if name == "" or "," in name:
            name = "name"
        if email == "" or "," in email or not len(email.split("/")) == email.count('@'):
            email = "email"
        file_identification_rewriting("./barcodes/barcodes.csv", barcode, barcode+","+name+","+email+"\n")
        return 0, ""
    except:
        error = traceback.format_exc()
        print(error)
        return 1, error

def main():
    login = False
    global window
    global password
    global monitor_width
    global monitor_height
    while True:
        format_dt_now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        final_send_csv_season = ["", "", ""]
        if os.path.isfile("./barcodes/csvlog.txt"):
            f = open('./barcodes/csvlog.txt', 'r')
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
                    status = status + "正しいバーコードを読み込んでください\nerror: "+error+"\n"
                elif result == 3:
                    status = status + "リストから名前が見つかりませんでした\n"
                elif result == 4:
                    status = status + "10分の動作は許されません\n"
                window["statusattendance"].update(status)
            except:
                error = traceback.format_exc()
                print(error)
                window["statusattendance"].update(status + "GUIで原因不明なエラーが発生しました\nerror : "+error)
            window["statusattendance"].update(status + "\n\nバーコードを読み込んでください")
            window["barcodeattendance"].update("")
        elif event == 'edit':
            status = values["statusedit"] + "\n"
            if login == False:
                status = status + "管理者ではありません\n"
                window["statusedit"].update(status)
                continue
            else:
                try:
                    result, error = edit(values["barcodeedit"], values["name"], values["email"])
                    if result == 0:
                        status = status + "編集しました\n"
                    elif result == 1:
                        status = status + "原因不明なエラーが発生しました\nエラーを報告しました\nerror: "+error+"\n"
                    elif result == 2:
                        status = status + "正しいバーコードを入力してください\n"
                    window["statusedit"].update(status)
                except:
                    error = traceback.format_exc()
                    print(error)
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
        elif event == 'sendcsv' or int(format_dt_now.split(" ")[0].split("/")[2]) >= etc[0] and int(format_dt_now.split(" ")[1].split(":")[0]) >= etc[1] and not [format_dt_now.split(" ")[0].split("/")[0], format_dt_now.split(" ")[0].split("/")[1]] == [final_send_csv_season[0], final_send_csv_season[1]]:
            if event == 'sendcsv' and login == False:
                window["statussendcsv"].update("管理者ではありません\n")
                continue
            try:
                data = get_personal_data(csv_file = "./barcodes/barcodes.csv")
                os.makedirs("csv", exist_ok=True)
                files = os.listdir("barcodes")
                arriving_files = []
                for i in files:
                    if ".txt" in i and i.replace(".txt", "").isdigit():
                        arriving_files.append(i)
                for i in arriving_files:
                    name = data[i.replace(".txt", "")][0]
                    with open("barcodes/"+i, encoding="utf-8") as f:
                        text_list = f.readlines()
                    text = "時間,種類\n"
                    for j in text_list:
                        text = text + j.replace(":", "年", 1).replace(":", "月", 1).replace(":", "日", 1).replace("/0", ",登校").replace("/1", ",下校")
                    with open("./csv/"+name+"-"+i.replace(".txt", ".csv"), mode='w', encoding="utf-8") as f:
                        f.write(text)
                    with open("./barcodes/old-"+format_dt_now.split(" ")[0].split("/")[0]+"-"+format_dt_now.split(" ")[0].split("/")[1]+"-"+i, mode='w', encoding="utf-8") as f:
                        f.write("".join(text_list))
                    with open("barcodes/"+i, mode="w", encoding="utf-8") as f:
                        f.write("")
                zp = zipfile.ZipFile("csv.zip", "w")
                for i in os.listdir("csv"):
                    zp.write("csv/"+i)
                zp.close()
                sendgmailfile(mail_address, app_pass, [mail_address], "CSV", "CSV", ["csv.zip"])
                shutil.rmtree("csv")
                os.remove("csv.zip")
                if login == False:
                    with open(f'./barcodes/csvlog.txt', mode='a', encoding="utf-8") as f:
                        f.write("\n"+format_dt_now.split(" ")[0])
                window["statussendcsv"].update("送信しました")
            except:
                error = traceback.format_exc()
                print(error)
                window["statussendcsv"].update("原因不明なエラーが発生しました\nerror : "+error)
        elif event == 'login':
            if login == True:
                window["statuslogin"].update("すでにログインしています")
                continue
            elif values["password"] == "":
                window["statuslogin"].update("パスワードが空です")
                continue
            input_password = hashlib.sha256(values["password"].encode()).hexdigest()
            if password == input_password:
                window["password"].update("")
                window["statuslogin"].update("ログインしました")
                window["editab"].update(visible=True)
                window["csvviewtab"].update(visible=True)
                window["settingtab"].update(visible=True)
                window["directeditfiletab"].update(visible=True)
                login = True
            else:
                window["statuslogin"].update("パスワードが違います")
                continue
            with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                text_list = f.readlines()
            window["csv"].update("".join(text_list[1:]).replace(",name,email", ",空"))
            if values["selectfile"] == "barcodes.csv":
                window["inputedit"].update("".join(text_list))
        elif event == 'logout':
            if login != True:
                window["statuslogin"].update("ログインしていません")
                continue
            login = False
            window["editab"].update(visible=False)
            window["csvviewtab"].update(visible=False)
            window["settingtab"].update(visible=False)
            window["directeditfiletab"].update(visible=False)
            window["statuslogin"].update("ログアウトしました")
            window["inputedit"].update("")
            window["csv"].update("")
        elif event == "passwordsetting":
            try:
                if login != True:
                    window["settingstatus"].update("管理者ではありません\n")
                    continue
                input_password = hashlib.sha256(values["repassword"].encode()).hexdigest()
                file_identification_rewriting("./barcodes/setting.ini", "password", "password = "+input_password+"\n")
                window["repassword"].update("")
                window["settingstatus"].update("パスワードを変更しました 再起動してください\n")
            except:
                error = traceback.format_exc()
                print(error)
                window["settingstatus"].update("原因不明なエラーが発生しました\nerror : "+error+"\n")
        elif event == "selectfile":
            with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                text = f.read()
            window["inputedit"].update(text)
        elif event == "directedit":
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                continue
            try:
                if not "." in values["selectfile"]:
                    window["statusdirectedit"].update("選択したファイル名が空です")
                    continue
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                    text = f.read()
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8", mode="w") as f:
                    f.write(values["inputedit"])
                if not values["inputedit"] == text:
                    with open(f"barcodes/"+values["selectfile"]+".backup", encoding="utf-8", mode="w") as f:
                        f.write(text)
                if values["selectfile"] == "barcodes.csv":
                    window["csv"].update(values["inputedit"].replace(",name,email", ",空"))
                window["statusdirectedit"].update("書き換えに成功しました\n再起動してください\n(一個前のバックアップはbarcodes/"+values["selectfile"]+".backupにあります)")
            except:
                error = traceback.format_exc()
                print(error)
                window["statusdirectedit"].update("書き換えに失敗しました")
        elif event == "regetfile":
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                continue
            try:
                if not "." in values["selectfile"]:
                    window["statusdirectedit"].update("選択したファイル名が空です")
                    continue
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                    text = f.read()
                window["inputedit"].update(text)
                window["statusdirectedit"].update("ファイルを再取得しました")
            except:
                error = traceback.format_exc()
                print(error)
                window["statusdirectedit"].update("ファイルの再取得に失敗しました")


    window.close()

if __name__ == "__main__":
    main()