import configparser, tkinter, traceback, datetime, smtplib, shutil, hashlib, zipfile, csv, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
import PySimpleGUI as sg

PORT = 52268

mode = ""

ini = configparser.ConfigParser()
path = os.getcwd() + os.sep + 'barcodes/setting.ini'
ini.read(path, 'UTF-8')

password = ini["admin"]["password"]
mail_address = ini["gmail"]["mail_address"]
app_pass = ini["gmail"]["app_pass"]
title = [ini["title_setting"]["arriving"], ini["title_setting"]["gohome"]]
text = [ini["text_setting"]["arriving"], ini["text_setting"]["gohome"]]

while True:
    try:
        root = tkinter.Tk()

        monitor_height, monitor_width = root.winfo_screenheight(), root.winfo_screenwidth()
        root.destroy()
        sg.theme("SystemDefault1")
        layout_attendance = [
                [sg.Text("Yes Barcode System", font=('Arial',15))],
                [sg.Text("バーコード:"), sg.Input(key="barcodeattendance")],
                [sg.Multiline(key="statusattendance", expand_x=True, expand_y=True,  pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="バーコードを読み込んでください\n", autoscroll=True)]
                ]

        layout_edit = [
                [sg.Text('内容変更', font=('Arial',15))],
                [sg.Text('バーコード'), sg.InputText(key='barcodeedit')],
                [sg.Text('名前'), sg.InputText(key='name')],
                [sg.Text('Email("/"区切り)'), sg.InputText(key='email')],
                [sg.Multiline(key="statusedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="情報を書いてください\n", autoscroll=True)],
                [sg.Button('変更',key='edit')]
                ]
        layout_csv_view = [
                [sg.Text('CSV VIEW', font=('Arial',15)), sg.Button('CSVファイル送信',key='sendcsv'), sg.Text(key="statussendcsv")],
                [sg.Text('空はいま登録されてないバーコードです')],
                [sg.Multiline(key="csv", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, font=('Arial',15), autoscroll=True)]
                ]
        layout_setting = [
                [sg.Text('設定', font=('Arial',15))],
                [sg.Text('パスワード設定')],
                [sg.Text('パスワード再設定'), sg.Input(key="repassword"), sg.Button("設定", key="passwordsetting")],
                [sg.Text(key="settingstatus")]
                ]
        layout_main = [
                [sg.Text("管理者パスワード"), sg.Input(key="password"), sg.Text(key="statuslogin")],
                [sg.Button("ログイン", key="login"), sg.Button("ログアウト", key="logout"), sg.Button("終了", key="exit")],
                [sg.TabGroup
                ([[sg.Tab("勤怠", layout_attendance),
                sg.Tab("編集", layout_edit),
                sg.Tab("CSV閲覧", layout_csv_view),
                sg.Tab("設定", layout_setting)]], size=(monitor_width, monitor_height))]
                ]

        window = sg.Window("Yes Barcode System", layout_main, margins=(0,0), size=(monitor_width, monitor_height), resizable=True, finalize=True, no_titlebar=True, location=(0,0)).Finalize()
        window.Maximize()
        window["barcodeattendance"].set_focus()
        break
    except Exception as e:
        print(e)
        continue

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

        # 本文の追加
        _msg.attach(MIMEText(text, "plain"))

        # 添付ファイルの追加
        for filename in file:
            with open(filename, 'rb') as _f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(_f.read())

            # base64 encode
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= {}'.format(filename))

            _msg.attach(part)

        # セキュアなSSL接続で送信
        context = ssl.create_default_context()

        _smtp = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465, timeout=10, context=context)
        _smtp.login(user=mail_address, password=app_pass)
        _smtp.sendmail(mail_address, i, _msg.as_string())
        _smtp.close()

def which_arriving_gohome(barcode : str, dt = datetime.datetime.now(), arriving_deadline_time = 19, arriving_isolation_period_min = 10):
    """0 = arriving, 1 = gohome"""
    type = None
    format_dt_now = dt.strftime('%Y:%m:%d:%H:%M:%S')
    if os.path.isfile("./barcodes/"+barcode+".txt"):
        with open("./barcodes/"+barcode+".txt", 'r', encoding="utf-8") as f:
            for line in f:  pass
            last_line = line.split("/")
            last_line_time = last_line[0].split(":")
            last_line_which_one = last_line[1]
            if last_line_time[:3] == format_dt_now.split(":")[:3]:
                if last_line_time[3] == format_dt_now.split(":")[3] and int(format_dt_now.split(":")[4]) - int(last_line_time[4]) <= arriving_isolation_period_min:
                    return None, 1
                if last_line_which_one == "0" or int(last_line_time[3]) >= arriving_deadline_time:
                    type = 1
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
            if to == "" or not len(to) == data[barcode][1].count('@'):
                return 3, ""
            name = data[barcode][0]
            if name == "":
                return 4, ""
        except:
            error = traceback.format_exc()
            print(error)
            return 2, error
        type, result = which_arriving_gohome(barcode)
        if result == 1:
            return 5, ""
        if not to == "":
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>{0}</title>
</head>
<body>
    <h1>YES Barcode System</h1>
    {1}
    <p>バグがありましたら</p>
    <a href="mailto:solothunder.autoer@gmail.com">solothunder.autoer@gmail.com</a>
    <p>にご連絡ください</p>
</body>
</html>"""
            if type == 0:
                send_gmail(mail_address, app_pass, to, title[0], html.format(title[0], text[0].replace("/name/", name)))
            else:
                send_gmail(mail_address, app_pass, to, title[1], html.format(title[1], text[1].replace("/name/", name)))
        with open("./barcodes/"+barcode.replace(" ", "")+".txt", mode='a', encoding="utf-8") as f:
            f.write(f'\n{format_dt_now}/{str(type)}')
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
        if not barcode in barcodes:
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
    mode = "main"
    login = False
    global window
    global password
    global monitor_width
    global monitor_height
    while True:
        event, values = window.read(timeout=50)
        if event == sg.WIN_CLOSED:
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
                    status = status + "リストからメールが見つかりませんでした\n"
                elif result == 4:
                    status = status + "リストから名前が見つかりませんでした\n"
                elif result == 5:
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
        elif event == 'sendcsv':
            if login == False:
                window["statussendcsv"].update("管理者ではありません\n")
                continue
            try:
                data = get_personal_data(csv_file = "./barcodes/barcodes.csv")
                os.makedirs("csv", exist_ok=True)
                files = os.listdir("barcodes")
                arriving_files = []
                for i in files:
                    if ".txt" in i:
                        arriving_files.append(i)
                for i in arriving_files:
                    name = data[i.replace(".txt", "")][0]
                    with open("barcodes/"+i, encoding="utf-8") as f:
                        text_list = f.readlines()
                    text = "時間,種類\n"
                    for j in text_list[1:]:
                        text = text + j.replace(":", "年", 1).replace(":", "月", 1).replace(":", "日", 1).replace("/0", ",登校").replace("/1", ",下校")
                    with open("./csv/"+name+"-"+i.replace(".txt", ".csv"), mode='w', encoding="utf-8") as f:
                        f.write(text)
                zp = zipfile.ZipFile("csv.zip", "w")
                for i in os.listdir("csv"):
                    zp.write("csv/"+i)
                zp.close()
                sendgmailfile(mail_address, app_pass, [mail_address], "CSV", "CSV", ["csv.zip"])
                shutil.rmtree("csv")
                os.remove("csv.zip")
                window["statussendcsv"].update("送信しました\n")
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
                login = True
            else:
                window["statuslogin"].update("パスワードが違います")
                continue
            with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                text_list = f.readlines()
            window["csv"].update("".join(text_list[1:]).replace(",name,email", ",空"))
        elif event == 'logout':
            if login != True:
                window["statuslogin"].update("ログインしていません")
                continue
            login = False
            window["statuslogin"].update("ログアウトしました")
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
        elif event == "exit":
            return

    window.close()

if __name__ == "__main__":
    main()