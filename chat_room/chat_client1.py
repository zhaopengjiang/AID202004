"""
chat room 练习客户端
"""
import re
import sys
from socket import *
from multiprocessing import *

# 服务端地址
ADDRESS = ('127.0.0.1', 1949)

# 1,judge进入聊天室
def login(udp_client) -> str:
    """

    :param udp_client:
    :return: 返回用户名
    """
    while True:
        n = input("Name(不支持一些特殊字符):")
        n1 = re.findall(r"\w+", n)
        name = ''.join(n1)
        if len(name) > 10:
            print("名字超过界限,请重新输入.")
            continue
        message = 'L ' + name  # 根据协议整理消息发送格式  L name
        udp_client.sendto(message.encode(), ADDRESS)
        data, add = udp_client.recvfrom(24)
        if data.decode() == 'OK':
            print('进入聊天室')
            return name
        else:
            print('该用户已存在')


# 2,发送消息
def send_message(udp_socket, name):
    # 循环发送消息
    while True:
        try:
            message = input(">>>")
        except:
            message = 'exit()'
        if message == 'exit()':
            udp_socket.sendto(f"D {name}".encode(), ADDRESS)
            sys.exit("退出聊天室")  # 父进程退出,将其交给系统处理回收
        msg = "C %s %s" % (name, message)
        udp_socket.sendto(msg.encode(), ADDRESS)


# 接收消息
def receive_message(sock):
    while True:
        data, add = sock.recvfrom(1024 * 4)
        message = data.decode().split(" ", 1)
        # 协议约束 C 是内容(content)
        if message[0] == "C":
            mes = "\n" + message[1] + "\n>>>"
            print(mes, end="")
        # 协议约束 I 进入或退出消息
        if message[0] == "I":
            mes = "\n" + message[1].center(50, " ") + "\n>>>"
            print(mes, end="")


def main():
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    name = login(udp_socket)  # type:str
    # 创建子进程,接收消息
    p = Process(target=receive_message, args=(udp_socket,))
    p.daemon = True  # 父进程退出时,子进程也结束
    p.start()
    # 发送消息
    send_message(udp_socket, name)


if __name__ == '__main__':
    main()
