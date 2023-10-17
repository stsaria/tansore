import threading, traceback, hashlib, random, time, csv, sys, os
import aspose.barcode as barcode
import csv

barcode_number = 100
data = []

end = False

def install_print():
    print("Install ", end="")
    while not end:
        print(".", end="")
        time.sleep(1)

def main():
    global end
    print("Note: This English text was translated from Japanese by Deepl\n")
    if not os.path.isfile("./main.py"):
        print("Run install.py in the tansole directory")
    file = input("Please enter the CSV file containing personal information : ")
    location = input("Enter the name of the facility where the system is located : ")
    password = hashlib.sha256(input("Please enter new administrator password : ").encode()).hexdigest()
    install_print_thread = threading.Thread(target=install_print)
    install_print_thread.start()
    try:
        os.makedirs("barcodes", exist_ok=True)
        os.makedirs("linux-file", exist_ok=True)
        with open(file, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                data.append(["", row[0], row[1]])
        for i in range(100 - len(data)):
            data.append(["", "name", "email"])
        codes = []
        for i in range(len(data)):
            code = ""
            for j in range(10):
                while True:
                    code = code + str(random.randrange(10))
                    if code in codes:
                        continue
                    else:
                        break
            data[i][0] = code
            codes.append(code)
        for i in range(len(data)):
            generator = barcode.generation.BarcodeGenerator(barcode.generation.EncodeTypes.CODE_39_STANDARD)
            generator.code_text = codes[i]
            generator.parameters.caption_above.text = data[i][1]
            generator.parameters.caption_above.visible = True
            generator.save(f"./barcodes/{codes[i]}-barcode.png")
        with open(f'./barcodes/setting.ini', mode='w', encoding="utf-8") as f:
            f.write(f"[admin]\npassword = {password}\n[gmail]\nmail_address = \napp_pass =\n[title_setting]\narriving = 到着報告\ngohome = 出発報告\n[text_setting]\narriving = /name/さんが{location}に到着しました\ngohome = /name/さんが{location}を出発しました\n[etc]\nlocation = {location}\nsend_csv_deadline_day = 26\nsend_csv_deadline_time = 8\narriving_deadline_time = 18\narriving_isolation_period_min = 10")
        with open(f'./barcodes/barcodes.csv', mode='w', encoding="utf-8") as f:
            f.write('barcode,name,email\n')
        for i in data:
            with open(f'./barcodes/barcodes.csv', mode='a', encoding="utf-8") as f:
                f.write(f'{i[0]},{i[1]},{i[2]}\n')
        with open(f'./linux-file/tansore.service', mode='w', encoding="utf-8") as f:
            f.write(f"""[Unit]
Description = Tansore System
After = graphical.target
Wants = graphical.target

[Service]
user = {os.getlogin()}

WorkingDirectory={os.path.abspath(".")}

Restart=always

Environment="DISPLAY=:0.0"
Environment="XAUTHORITY=/home/{os.getlogin()}/.Xauthority"

#ExecStartPre = /usr/bin/printenv
ExecStart=/usr/bin/python {os.path.abspath(".")}/main.py %i

[Install]
WantedBy = graphical.target""")
        with open(f'./linux-file/update-cron.d.root', mode='w', encoding="utf-8") as f:
            f.write(f"""0 19 * * * root systemctl stop tansore && rm {os.path.abspath(".")}/main.py && wget -P {os.path.abspath(".")} https://github.com/stsaria/tansore/raw/main/main.py && systemctl start tansore
0 19 * * * root systemctl stop tansore && rm {os.path.abspath(".")}/install.py && wget -P {os.path.abspath(".")} https://github.com/stsaria/tansore/raw/main/install.py && systemctl start tansore""")
    except:
        print(" Error\n")
        error = traceback.format_exc()
        print(error)
        return 1
    end = True
    print(" Success\nNote: You need to fill in the ini file with your or group\ngmail address and the app password (Google API password) in order to send the email\nservice file and cron file (root) created in [linux-file] directory")
    return 0

if __name__ == "__main__":
    sys.exit(main())