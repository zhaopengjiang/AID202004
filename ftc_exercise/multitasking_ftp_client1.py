"""
multitasking ftp client
"""
import sys
import time
from socket import *

ADDRESS = ("127.0.0.1", 1949)


class FTPClient:
    def __init__(self, sock):
        self.sock = sock

    # 请求文件列表
    def do_list(self):
        self.sock.send(b"LIST")  # 发送请求
        result = self.sock.recv(128).decode()  # 等待回复
        if result == 'OK':
            # 接收文件列表
            while True:
                file = self.sock.recv(1024).decode()
                if file == "##":
                    break
                print(file)
        else:
            # 结束
            print("文件库为空")

    # 处理下载
    def do_down(self):
        filename = input("请输入文件名:")
        msg = ("DOWN " + filename)
        self.sock.send(msg.encode())
        result = self.sock.recv(128).decode()
        print(result)
        if result == "OK":
            file = open(filename, "wb")
            while True:
                data = self.sock.recv(1024 * 6)
                if data == b"##":
                    print("文件下载成功")
                    break
                file.write(data)
            file.close()
        else:
            print("没有该文件.")
            return

    # 处理上传
    def do_up(self):
        path = input("请输入文件路径:")
        # 客户端做一下判断看文件是否存在
        try:
            file = open(path, 'rb')
        except:
            print("要上传的文件不存在")
            return
        # 提取文件名
        filename = path.split("/")[-1]
        # 发送请求
        msg = "UP " + filename
        self.sock.send(msg.encode())
        # 等待回复
        result = self.sock.recv(128).decode()
        # 根据服务端的回复来进行相应的
        if result == "OK":
            while True:
                data = file.read(1024 * 5)
                if not data:
                    time.sleep(0.1)
                    self.sock.send(b"##")
                    break
                self.sock.send(data)
            file.close()
            print(self.sock.recv(128).decode())
        else:
            print("该文件已存在.")

    # 退出
    def do_exit(self):
        self.sock.send(b"EXIT")
        self.sock.close()
        sys.exit("程序退出,欢迎下次使用")


def main():
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(ADDRESS)
    except ConnectionRefusedError as C:
        print("连接被拒绝.")
    ftp = FTPClient(sock)
    while True:
        print("命令选项".center(50, "="))
        print("***" + "list".center(46) + "***")
        print("***" + "down".center(46) + "***")
        print("***" + "up".center(46) + "***")
        print("***" + "exit".center(46) + "***")
        print("=" * 53)
        data = input(">>>")
        if data == "list":
            ftp.do_list()
        elif data == "down":
            ftp.do_down()
        elif data == "up":
            ftp.do_up()
        elif data == "exit":
            ftp.do_exit()
        else:
            print("没有该选项")


if __name__ == '__main__':
    main()
