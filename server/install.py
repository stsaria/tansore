import random, csv, os
import aspose.barcode as barcode
import csv

data = []

os.makedirs("barcodes", exist_ok=True)

file = input("CSVFILE : ")
location = input("LOCATION : ")

with open(file, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        data.append(["", row[0], row[1]])

codes = []
for i in data:
    code = ""
    for j in range(10):
        while True:
            code = code + str(random.randrange(10))
            if code in codes:
                continue
            else:
                break
    i[0] = code
    codes.append(code)

for i in codes:
    generator = barcode.generation.BarcodeGenerator(barcode.generation.EncodeTypes.CODE_39_STANDARD)
    generator.code_text = i
    generator.save(f"./barcodes/{i}-barcode.png")

with open(f'./barcodes/setting.ini', mode='w', encoding="utf-8") as f:
    f.write(f"[gmail]\nmail_address = \napp_pass =\n[title_setting]\nattendance = 到着報告\ngohome = 出発報告\n[text_setting]\nattendance = /name/さんが{location}に到着しました\ngohome = /name/さんが{location}を出発しました")

with open(f'./barcodes/barcodes.csv', mode='w', encoding="utf-8") as f:
    f.write('barcode,name,email\n')

for i in data:
    with open(f'./barcodes/barcodes.csv', mode='a', encoding="utf-8") as f:
        f.write(f'{i[0]},{i[1]},{i[2]}\n')