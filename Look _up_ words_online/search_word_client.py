"""
v:界面显示层
"""
from socket import *
import sys

# 服务器地址
ADDR = ("127.0.0.1", 8888)


# 注册新账号
def register(sockfd):
    while True:
        name = input("请输入账户名字>>")
        passwd = input("请设置账户密码>>")
        if " " in name or " " in passwd:
            print("用户名和密码不能包含空格.")
            continue
        data = "R %s %s" % (name, passwd)
        sockfd.send(data.encode())
        result = sockfd.recv(1024).decode()
        if result == "OK":
            print("账号注册成功,请保护好密码.")
            return name
        else:
            print("账号注册失败,用户名已存在.")
            return False


# 登录
def log_in(sockfd):
    while True:
        name = input("请输入用户名字>>")
        passwd = input("请输入用户密码>>")
        if " " in name or " " in passwd:
            print("用户名和密码不能包含空格.")
            continue
        data = "L %s %s" % (name, passwd)
        sockfd.send(data.encode())
        result = sockfd.recv(1024).decode()
        if result == "OK":
            print("登录成功")
            return name
        else:
            print("登录失败")
            return False


# 查看单词
def find_word(sockfd, name):
    while True:
        word = input("请输入单词>>")
        if word == "##":
            break
        msg = "F %s %s" % (name, word)
        sockfd.send(msg.encode())
        data = sockfd.recv(1024).decode()
        print(data)


# 查看历史记录
def view_histories_log(sockfd, name):
    msg = "V " + name
    sockfd.send(msg.encode())  # 发送请求
    # 循环接受,由于不能确认次数所以使用while
    while True:
        data = sockfd.recv(1024 * 2).decode()
        if data == "##":
            break
        print(data)


# 显示二级菜单
def display_menus(sockfd, name):
    while True:
        print("""
        ===============command===============
        1.查询单词    2.查看历史记录    3.注销
        =====================================
        """)
        cmd = input("请输入选项:")
        if cmd == '1':
            find_word(sockfd, name)
        elif cmd == "2":
            view_histories_log(sockfd, name)
        elif cmd == "3":
            break
        else:
            print("请输入正确命令。")


# 连接服务端
def main():
    # 创建套接字
    try:
        sockfd = socket()
        sockfd.connect(ADDR)
    except:
        print("请检查你的网络后重试！")
        return
    try:
        # 进入一级界面
        while True:
            print("""
            ===========Welcome===========
             1.注册     2.登录     3.退出
            =============================
            """)
            cmd = input("请输入选项:")
            if cmd == '1':
                name = register(sockfd)
                if name:
                    # 进入二级界面
                    display_menus(sockfd, name)
            elif cmd == "2":
                name = log_in(sockfd)
                if name:
                    # 进入二级界面
                    display_menus(sockfd, name)
            elif cmd == "3":
                sockfd.send(b"E")
                sys.exit("谢谢使用")
            else:
                print("请输入正确命令。")
    except Exception as e:
        print(e)
        print("由于同时人数过多导致服务器崩了.")


if __name__ == '__main__':
    main()  # 启动
