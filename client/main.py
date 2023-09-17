import keyboard, socket, time, sys

PORT = 52268

def create_client(ip,port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( (ip,port) )
    return client

def main():
    while True:
        try:
            print("バーコードを読み込んでください")
            barcode = ""
            while True:
                barcode = barcode + keyboard.read_key()
                if barcode:
                    if " " in barcode: break
            barcode = barcode.replace(" ", "")
            print("サーバーに接続しています\n30秒ほど掛かる可能性があります")
            con = create_client(sys.argv[1], PORT)
            print("サーバーに接続しました")
            print("バーコードを送信しています")
            con.send(barcode.encode('utf-8'))
            print("バーコードを送信しました")
            print("応答を待っています")
            while True:
                result = con.recv(1024).decode('utf-8')
                if not result:
                    continue
                print("応答を受け取りました")
                con.close()
                break
            match int(result):
                case 0:
                    print("勤怠しました")
                case 1:
                    print("原因不明なエラーが発生しました（サーバー）")
                case 2:
                    print("正しいバーコードを読み込んでください")
                case 3:
                    print("リストから名前が見つかりませんでした")
                case 4:
                    print("10分の勤怠は許されません")
            time.sleep(3000)
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        except ConnectionRefusedError:
            print("サーバーへの接続に失敗しました")
            continue
        except TimeoutError:
            print("サーバーでの通信でタイムアウトしました")
            continue
        except Exception: 
            print("原因不明なエラーが発生しました")
            continue

if __name__ == "__main__":
    main()