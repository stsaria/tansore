import readchar, socket, sys

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
                barcode = barcode + readchar.readchar()
                if barcode:
                    if " " in barcode: break
            barcode = barcode.replace(" ", "")
            print("サーバーに接続しています")
            con = create_client(sys.argv[1], PORT)
            con.send(barcode.encode('utf-8'))
            while True:
                result = con.recv(1024).decode('utf-8')
                if not result:
                    continue
                con.close()
                break
            match result:
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