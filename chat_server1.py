"""
author: Luck Old Boy
email: 2687945480@qq.com
time: 2020-06-13
env: Python3.6
socket and Process exercise
exercise_name: chat room exercise (server)
"""
from socket import *
from multiprocessing import Process, Queue

# 全局变量,服务端IP地址与端口号
HOST = '0.0.0.0'
PORT = 1949
ADDRESS = (HOST, PORT)
# 存储用户 {name:address}
user = {}


# 进行验证看该用户是否已经在聊天室中,不存在则将其添加在字典中
def do_login(udp_server, name: str, address):
    if name in user:
        udp_server.sendto(b'Fail', address)
    else:
        udp_server.sendto(b'OK', address)
        # 将用户添加到字典中
        user[name] = address
        # 通知所有人
        message = "I 欢迎 '%s' 进入聊天室" % name
        for i in user:
            udp_server.sendto(message.encode(), user[i])

    print(user)


# 处理聊天 约束C
def do_chat(udp_socket, name: str, content):
    # 　协议约束C空格开头发送　C 名字：内容
    msg = 'C %s: %s' % (name, content)
    for i in user:
        # 除去本人外所有人
        if i != name:
            udp_socket.sendto(msg.encode(), user[i])


# 退出聊天室 约束D
def do_exit(sock, agreement, name: str):
    if agreement == "A":
        message = "I %s" % name
    else:
        del user[name]
        # 协议约束D + content
        message = "I %s退出聊天室" % name
        # 通知聊天室里所有人
    for i in user:
        sock.sendto(message.encode(), user[i])


# 子进程函数
def do_request(udp_socket):
    # 循环接收消息
    while True:
        data, site = udp_socket.recvfrom(1024 * 4)
        # 最多切割两项
        message = data.decode().split(" ", 2)
        # 根据接受消息类型调用其他模块
        if message[0] == 'L':
            # message = ['L', 'name']
            do_login(udp_socket, message[1], site)
        elif message[0] == 'C':
            # message = ['C', 'name', 'content']
            do_chat(udp_socket, message[1], message[2])
        elif message[0] == "I" or message[0] == "A":  # "I" -> inform(通知)
            # message = ["I", "name"]
            do_exit(udp_socket, message[0], message[1])


def main():
    # 创建UDP连接
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    # 绑定地址
    udp_socket.bind(ADDRESS)
    p = Process(target=do_request, args=(udp_socket,))
    p.daemon = True
    p.start()
    # 父进程 发送管理员消息
    while True:
        try:
            content = input("管理员消息:")
            if content == 'quit':
                break
            msg = "A 管理员消息:" + content
            udp_socket.sendto(msg.encode(), ("127.0.0.1", 1949))  # 将消息发送给子进程
        except:
            print("服务器强制结束运行")
            break


if __name__ == '__main__':
    main()
