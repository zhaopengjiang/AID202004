"""
author: Zhao
email: ....
time: 2020-06-16
eve: Python3.6
This is multitasking ftp exercise
"""
# 导入模块
import sys, os
import time
from socket import *
from threading import Thread

# 全局变量
HOST = "0.0.0.0"
PORT = 1949
ADDRESS = (HOST, PORT)
FTP = '../6.10-11/'


class FTPServer(Thread):
    def __init__(self, conn_target):
        self.conn_target = conn_target
        super().__init__()

    # 处理客户端请求文件列表
    def do_list(self):
        # 判断文件库是否为空
        file_list = os.listdir(FTP)
        if not file_list:
            self.conn_target.send(b"FAIL")  # 列表为空
            return
        else:
            self.conn_target.send(b"OK")
            time.sleep(0.2)
            data = "\n".join(file_list)  # 将文件拼接
            self.conn_target.send(data.encode())
            time.sleep(0.1)
            self.conn_target.send(b"##")

    # 处理下载
    def do_down(self, filename):
        try:
            file = open(FTP + filename, 'rb')
            print(FTP + filename)
        except Exception as a:
            print(a)
            self.conn_target.send(b"FAIL")
            return
        self.conn_target.send(b"OK")
        time.sleep(0.1)
        while True:
            data = file.read(1024 * 5)
            if not data:
                time.sleep(0.1)
                self.conn_target.send(b"##")
                break
            self.conn_target.send(data)
        file.close()

    # 处理上传
    def dp_up(self, filename):
        # 判断该文件是否存在
        if os.path.exists(FTP + filename):
            self.conn_target.send(b"FAIL")
            return
        else:
            self.conn_target.send(b"OK")
            time.sleep(0.1)
            file = open(FTP + filename, "wb")
            while True:
                data = self.conn_target.recv(1024 * 6)
                if data == b"##":
                    file.close()
                    self.conn_target.send("\n文件上传成功".encode())
                    break
                file.write(data)

    def run(self):
        while True:
            data = self.conn_target.recv(1024 * 4).decode()
            message = data.split(" ", 1)
            # 处理退出
            if not data or message[0] == "EXIT":
                self.conn_target.close()
                break
            elif message[0] == "LIST":  # 查看
                self.do_list()
            elif message[0] == "DOWN":  # 下载
                self.do_down(message[1])
                print(message[1])
            elif message[0] == "UP":  # 上传
                self.dp_up(message[1])


def main():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(ADDRESS)
    sock.listen(20)

    while True:
        try:
            # 等待连接
            print("waiting from connect ...")
            conn, address = sock.accept()
            print("connect from", address)
        except:
            sock.close()
            sys.exit("退出服务器")
        # 创建线程
        t = FTPServer(conn)
        t.start()


main()
