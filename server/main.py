import configparser, threading, socket, datetime, smtplib, csv, os
from email.mime.text import MIMEText
from email.utils import formatdate

PORT = 52268

ini = configparser.ConfigParser()
path = os.getcwd() + os.sep + 'barcodes/setting.ini'
ini.read(path, 'UTF-8')

mail_address = ini["gmail"]["mail_address"]
app_pass = ini["gmail"]["app_pass"]
title = [ini["title_setting"]["attendance"], ini["title_setting"]["gohome"]]
text = [ini["text_setting"]["attendance"], ini["text_setting"]["gohome"]]

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

def which_arriving_gohome(barcode : str, dt = datetime.datetime.now(), arriving_deadline_time = 18):
    """0 = attendace, 1 = gohome"""
    type = None
    format_dt_now = dt.strftime('%Y:%m:%d:%H:%M:%S')
    if os.path.isfile("./barcodes/"+barcode+".txt"):
        with open("./barcodes/"+barcode+".txt", 'r', encoding="utf-8") as f:
            for line in f:  pass
            last_line = line.split("/")
            last_line_time = last_line[0].split(":")
            last_line_which_one = last_line[1]
            if last_line_time[:3] == format_dt_now.split(":")[:3]:
                if last_line_time[3] == format_dt_now.split(":")[3] and int(format_dt_now.split(":")[4]) - int(last_line_time[4]) <= 10:
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
            name = data[barcode][0]
            if name == "":
                return 3
        except Exception as e:
            return 2
        type, result = which_arriving_gohome(barcode)
        if result == 1:
            return 4
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
    except:
        return 1

def handle_client(client_socket, address):
    try:
        while True:
            barcode = client_socket.recv(1024).decode('utf-8')
            if not barcode:
                break
            else:
                result = attendance(barcode)
                if result != 0:
                    client_socket.send(f"ng/{result}".encode('utf-8'))
                    client_socket.close()
                else:
                    client_socket.send(f"ok".encode('utf-8'))    
                    client_socket.close()
                break
        client_socket.close()
        return 0
    except Exception as e:
        client_socket.close()
        return 1

def main(port = PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)
    try:
        while True:
            client_socket, address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()
    except KeyboardInterrupt:
        server_socket.close()

if __name__ == "__main__":
    main()