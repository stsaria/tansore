# Tansore -Attendance System-
## 注意
- このプログラム(GUI)の画面は画面サイズにより
収まりきらない可能性があります
- このプログラムのライセンスはLGPL v3.0です
ライセンスの詳細（文）はLICENSEファイルを確認してください
- このプログラムを導入する場合は必ずシステムを管理している人に許可を得てください
SystemdやCronは管理者権限を得ている人であることを前提で作成しています
- このプログラムを重要なこと（ミスが許されない記録）などに使用することは
おすすめできません（素直にちゃんとした会社のソフトを使いましょう）
## イメージ
### Windows (11)
![image](https://github.com/stsaria/tansore/assets/123633917/2fbffb39-ce2c-44df-a982-6c1ded10b8b4)
### Raspbian OS (Arm64 RaspberryPi 3B)
![image](https://github.com/stsaria/tansore/assets/123633917/35621a66-efdf-4fcb-a8fb-952222c3793f)
## 動作環境
### バージョン等
- Windows : 7 ~ 最新
- Linux (この例ではUbuntu) : Ubuntu 16.04 ~ 最新

- Python : 3.6以上
### 必要CPUの種類
- Windows(バーコード作成時) : x64, Amd64<br/>
- Linux(バーコード作成時) : x86, x64, Amd64<br/>

- Windows(バーコード作成後) : x86, x64, Amd64, Arm64<br/>
- Linux(バーコード作成後) : x86, x64, Amd64, Arm64(AArch64), Arm32(AArch32)<br/>
### 使用ライブラリ(非標準)
- PySimpleGUI<br/>
- aspose.barcode (任意)<br/>
- romkan (任意)
- tkinter (すでに入っている可能性があります)<br/>
### その他
- ネットワーク環境(テザリング可)<br/>
- 推奨Python : 3.7 ~ 最新
- 常識的な空き容量(HDD・SSD・SD・Emmc・USB)<br/>
- 確認済みCPU : x64, Amd64, Arm64(AArch64)<br/>
## セットアップ
- Githubなどからソースコードをダウンロード<br/>
- pipでライブラリをインストール<br/>
```
pip install aspose-barcode-for-python-via-net (任意)
pip install pysimplegui
pip install romkan (任意)
pip install tkinter または pytk または(すでに入っている可能性があります)
または
apt install python3-tk (apt権限が必須)
```
- 個人情報CSVファイルを作成(記述方法は以下)<br/>
```
名前,メールアドレス
abc,aaa@bbb.ccc
hoge,fuga@piyo.aho
```
- tansore.pyを起動して指示通りインストールする`python3 tansore.py --install`<br/>
- tansore.pyを起動して勤怠システムを使用する`python3 tansore.py`<br/>
- 必要があればcronやsystemdを設定する<br/>
## GUIでのマニュアル
### バーコードリーダーのセットアップ
- リーダーをコンピューターにつなぐ<br/>
- リーダーのマニュアルを見て、読み込み文字列の最後に半角スペースが出力されるように設定する<br/>
### 勤怠
- tansore.pyを起動して`python3 tansore.py`、そのままバーコードを読み取る<br/>
- "勤怠しました"と出たら成功です<br/>
### 管理者権限の取得
- バーコードファイルの作成時に設定したパスワードを入力してください<br/>
### CSVファイル関係
**管理者権限が必要です**<br/>
#### CSVファイルの閲覧
- 上のCSV閲覧のタブにファイルの内容が、書かれています<br/>
#### CSVファイルの編集(一人ずつ)
- CSV閲覧のタブにある"バーコード番号"をCSV編集のバーコードに入力して名前も入力します<br/>
- Emailアドレスは/(スラッシュ)区切りで、何個でもEmailアドレスを設定できます<br/>
- 最後に編集ボタンを押して"編集しました”と出たら成功です<br/>
**注:・何も入力しない場合は空になります**<br/>
**・BackUpファイルは一個しかありません**<br/>
**2回変えると一回目のデータは消えます**<br/>
### 直接でのファイルの編集
**管理者権限が必要です**<br/>
**直接でのファイルの編集は推奨しません**<br/>
- 直接編集のタブに移動します<br/>
- ファイルを選びます<br/>
- 編集が完了したら"書き換え"ボタンを押します<br/>
- "書き換えに成功しました"と出たら成功です(再起動をしてください)<br/>
- "再取得(巻き戻し)"を押すと今のファイルの状況を取得できます<br/>
### パスワードの再設定
**管理者権限が必要です**<br/>
- 設定のタブに移動します<br/>
- パスワード再設定の項目の入力箇所にパスワードを書いて<br/>
- 設定ボタンを押します<br/>
- "パスワードを変更しました"と出たら成功です(再起動をしてください)<br/>
### 勤怠情報の送信
**管理者権限が必要です**<br/>
**勤怠情報の送信は設定した日時で自動的に実行されます**<br/>
- CSV閲覧のタブに移動します<br/>
- "勤怠情報送信"ボタンを押します<br/>
- "送信しました"と出たら成功です<br/>
## ファイルの編集系
### iniファイルの編集
```
[admin]
password = SHA256のパスワード(改変はしないで)
[gmail]
mail_address = 送信先メールアドレス(Gmail)
app_pass = Gmailから取得したアプリパスワード(スペースなし)
[title_setting]
arriving = 到着時メールのタイトル(デフォルト:到着報告)
gohome = 出発時メールのタイトル(デフォルト:出発報告)
[text_setting]
arriving = 到着時メールの本文(/name/で名前)(デフォルト:/name/さんがyesに到着しました)
gohome = 出発時メールの本文(/name/で名前)(デフォルト:/name/さんがyesに出発しました)
[etc]
send_csv_deadline_day = 勤怠情報の締め切り日(デフォルト:26)
send_csv_deadline_time = 勤怠情報の締め切り時(デフォルト:8)
arriving_deadline_time = 到着の締め切り時(デフォルト:18)
arriving_isolation_period_min = 勤怠のクルータイム分(デフォルト:10)
```
