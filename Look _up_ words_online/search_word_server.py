"""
c:逻辑业务层
"""

import sys
import signal
from socket import *
from time import sleep
from search_modle import *
from multiprocessing import Process

# 全局变量
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST, PORT)

# 实例化数据库对象
db = Database()


# 注册
def do_register(connfd, name, passwd):
    # 判断可否注册 --》 数据库处理 ->调用数据库方法解决问题
    # 返回True表示可以注册 False 表示注册不成功

    # 得到结果
    if db.register(name, passwd):
        connfd.send(b"OK")
    else:
        connfd.send(b"Fail")


# 登录
def do_log_in(connfd, name, passwd):
    if db.log_in(name, passwd):
        connfd.send(b"OK")
    else:
        connfd.send(b"Fail")


# 查找单词
def do_find_word(connfd, name, word):
    # 添加历史记录
    db.add_history_log(name, word)
    # 获取查询结果,分情况处理,有结果则msg为真,没有msg则返回None
    msg = db.find_word(word)
    if msg:
        data = "%s : %s" % (word, msg)
    else:
        data = "%s : Not Found." % word
    connfd.send(data.encode())  # 将结果发送


# 查看历史记录
def do_hitory_log(connfd, name):
    data = db.view_history_log(name)
    # data --> ((name, word, datetime),()...)
    if data[0][1]:
        for i in data:
            message = "%-10s %-10s %-s" % i
            connfd.send(message.encode())
            sleep(0.1)  # tcp传输防止粘包
    else:
        connfd.send("没有查询记录.".encode())
        sleep(0.1)
    connfd.send(b"##")


# 处理客户端请求的进程
def handle(connfd):
    db.cursor()  # 每个子进程创建自己的游标
    # 接收某一个客户端的各种请求，分情况讨论处理 --> 采用总分模式
    while True:
        data = connfd.recv(1024).decode()
        if not data:
            break
        data = data.split(" ", 2)
        if not data or data == "E":  # 退出
            # 客户端退出
            break
        elif data[0] == "R":  # 注册新用户
            # data --> ["R", "name", "passwd"]
            do_register(connfd, data[1], data[2])
        elif data[0] == "L":  # 登录
            # data --> ["L", "name", "passwd"]
            do_log_in(connfd, data[1], data[2])
        elif data[0] == "F":  # 查询单词
            # data --> ["F", "name", "word"]
            do_find_word(connfd, data[1], data[2])
        elif data[0] == "V":  # 查看历史记录
            # data --> ["F", "name"]
            do_hitory_log(connfd, data[1])
    # 关闭子进程对应的资源
    connfd.close()
    db.cur.close()


# 网络并发模型
def main():
    # 创建tcp套接字
    sockfd = socket()
    sockfd.bind(ADDR)

    sockfd.listen(5)
    print("Listen the port %d" % PORT)

    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # 循环等待客户端连接
    while True:
        try:
            connfd, addr = sockfd.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            db.close()  # 关闭数据库连接
            sockfd.close()
            sys.exit("服务端退出")

        # 客户端连接则创建进程
        p = Process(target=handle, args=(connfd,))
        p.daemon = True
        p.start()


if __name__ == '__main__':
    main()  # 启动
