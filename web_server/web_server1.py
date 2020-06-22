"""
multitasking http exercise

IO多路复用与http训练
"""
import re
from socket import *
from select import select


class WebServer:
    def __init__(self, host="0.0.0.0", port=2697, html=None):
        self.host = host
        self.port = port
        self.html = html
        # IO多路复用准备  --> 设置关注列表为实例变量（属性）
        self._rlist = []
        self._wlist = []
        self._xlist = []
        # 调用创建套接字方法,初始化创建
        self._create_socket()
        self._bind()

    # 创建套接字,设置IO事假为非阻塞事件
    def _create_socket(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setblocking(False)

    # 绑定套接字
    def _bind(self):
        self.sock.bind((self.host, self.port))

    # 客户端请求具体处理方法
    def _handle(self, connfd):
        # 接受来自客户端的http请求(接受消息的大小最好大一点,以免连接人数过多发送内容太大挤爆服务端)
        request = connfd.recv(1024*10).decode()
        # print(request)
        # 解析http请求行的内容,获取请求类型与内容(使用正则)
        pattern = r"[A-Z]+\s+(?P<info>/\S*)"
        result = re.match(pattern, request)  # 匹配得到match对象,没有内容则返回None
        # 多情景进行
        if result:  # 如果提取到内容
            # 提取请求内容
            info = result.group("info")
            print("请求内容:", info)
            # 进一步进行判别,按照客户提供的请求返回相应的网页内容
            self._get_html(connfd, info)
        # 如果没有提取到内容(可能客户端断开连接,格式错误....)
        else:
            # 关闭客户端连接,取消关注
            connfd.close()
            self._rlist.remove(connfd)
            return  # 退出本次进行下个就绪事假

    # 组织网页数据给客户端回复(进行响应)
    def _get_html(self, connfd, info):
        # 进行请求内容的进一步判读,是否是主页,获取文件内容的详细地址
        if info == "/":
            filename = self.html + "/index.html"
        else:
            filename = self.html + info
        # 进行异常处理保证程序按流程走下去
        try:
            fd = open(filename, "rb")  # 以二进制模式打开
        except:
            # 请求的网页不存在
            response = "HTTP/1.1 404 Not found\r\n"  # 响应行
            response += "Content-Type:text/html\r\n"  # 响应头
            response += "\r\n"  # 空行
            response += "<h1>Sorry not found content.<h1>"  # 响应体
            response = response.encode()  # 转化为字节串(bytes)
        else:
            # 请求的内容存在
            data = fd.read()
            response = "HTTP/1.1 200 OK\r\n"  # 响应行
            response += "Content-Type:text/html\r\n"  # 响应头(内容类型)
            response += "Content-Length:%d\r\n" % len(data)  # 响应头(获取内容大小)
            response += "\r\n"  # 空行
            response = response.encode() + data  # 响应体
            fd.close()  # 关闭打开的文件
        finally:
            connfd.send(response)  # 发送响应结果给客户端

    # 启动方法
    def start(self):
        # 设置套接字监听队列
        self.sock.listen(12)
        print("Listen to the port %d" % self.port)
        # IO多路复用, 将监听套接字对象加入关注列表中
        self._rlist.append(self.sock)
        while True:
            # 对IO事件进行关注
            rs, ws, xs = select(self._rlist, self._wlist, self._xlist)
            # 总分模式,分情况进行
            for r in rs:
                # 如果IO就绪事件是self.sock(监听套接字)
                if r is self.sock:
                    cli_conn, addr = r.accept()
                    print("Connect from", addr)
                    # 将客户端连接套字设置为非阻塞ＩＯ事件
                    cli_conn.setblocking(False)
                    # 将其加入到读关注列表中
                    self._rlist.append(cli_conn)
                # 如果不是监听套接字(因为关注列表中只有两种类型监听套接字与
                # 客户端连接套接字所以不用考虑其他情况)按照客户端连接套接字进行
                else:
                    # 具体处理客户端请求
                    try: # 做个异常处理,如果客户端掉线或崩了,则关闭连接
                        self._handle(r)  # 将就绪客户端连接传入
                    except:
                        r.close()
                        self._rlist.remove(r)


if __name__ == '__main__':
    # 前端服务器启动方法
    try:
        httpd = WebServer(host="0.0.0.0", port=2697, html="./static")
        httpd.start()
    except KeyboardInterrupt as e:
        print("服务器退出")
