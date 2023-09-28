import random, csv, os, hashlib
import aspose.barcode as barcode
import csv

barcode_number = 100
data = []

os.makedirs("barcodes", exist_ok=True)

file = input("CSVFILE : ")
location = input("LOCATION : ")
password = hashlib.sha256(input("PASSWORD : ").encode()).hexdigest()

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
    f.write(f"[admin]\npassword = {password}\n[gmail]\nmail_address = \napp_pass =\n[title_setting]\narriving = 到着報告\ngohome = 出発報告\n[text_setting]\narriving = /name/さんが{location}に到着しました\ngohome = /name/さんが{location}を出発しました")

with open(f'./barcodes/barcodes.csv', mode='w', encoding="utf-8") as f:
    f.write('barcode,name,email\n')

for i in data:
    with open(f'./barcodes/barcodes.csv', mode='a', encoding="utf-8") as f:
        f.write(f'{i[0]},{i[1]},{i[2]}\n')