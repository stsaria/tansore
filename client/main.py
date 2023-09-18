import keyboard, socket, time, sys
import PySimpleGUI as sg

sg.theme("SystemDefault1")

layout = [
    [sg.Text("Yes Barcode System", font=('Arial',15))],
    [sg.Text("バーコード:"), sg.Input(key="barcode")],
    [sg.Multiline(key="status", pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="バーコードを読み込んでください", autoscroll=True)]
    ]

window = sg.Window("Yes Barcode System", layout, margins=(0,0), resizable=True, finalize=True, no_titlebar=True, location=(0,0)).Finalize()
window.Maximize()

window["status"].expand(expand_x=True, expand_y=True)
window["barcode"].set_focus()

PORT = 52268

def create_client(ip,port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( (ip,port) )
    return client

def send(barcode, values):
    try:
        status = values["status"] + "\n"
        status = status + "サーバーに接続しています\n30秒ほど掛かる可能性があります\n"
        window["status"].update(status)
        con = create_client(sys.argv[1], PORT)
        status = status + "サーバーに接続しました\nバーコードを送信しています\n"
        window["status"].update(status)
        con.send(barcode.encode('utf-8'))
        status = status + "バーコードを送信しました\n応答を待っています\n"
        window["status"].update(status)
        while True:
            result = con.recv(1024).decode('utf-8')
            if not result:
                continue
            status = status + "応答を受け取りました\n"
            window["status"].update(status)
            con.close()
            break
        if result == 0:
            status = status + "勤怠しました\n"
        elif result == 1:
            status = status + "原因不明なエラーが発生しました（サーバー）\n"
        elif result == 2:
            status = status + "正しいバーコードを読み込んでください\n"
        elif result == 3:
            status = status + "リストから名前が見つかりませんでした\n"
        elif result == 4:
            status = status + "10分の勤怠は許されません\n"
        window["status"].update(status)
        return status
    except ConnectionRefusedError:
        status = status + "サーバーへの接続に失敗しました\n"
        window["status"].update(status)
        return status
    except TimeoutError:
        status = status + "サーバーでの通信でタイムアウトしました\n"
        window["status"].update(status)
        return status
    except: 
        status = status + "原因不明なエラーが発生しました\n"
        window["status"].update(status)
        return status

def main():
    while True:
        event, values = window.read(timeout=50)
        if event == sg.WIN_CLOSED:
            break
        elif " " in values["barcode"]:
            result = send(values["barcode"].replace(" ", ""), values)
            window["barcode"].update(values["barcode"].replace(" ", ""))
            window["status"].update(result + "\n\nバーコードを読み込んでください")

    window.close()

if __name__ == "__main__":
    main()