"""
m:数据模型层
"""
import pymysql


# 数据库功能写在类中
class Database:
    def __init__(self):
        self.db = pymysql.connect(host="localhost",
                                  port=3306,
                                  user="root",
                                  password="123456",
                                  database="dict",
                                  charset="utf8")

    # 创建游标
    def cursor(self):
        self.cur = self.db.cursor()

    # 关闭数据库连接
    def close(self):
        self.db.close()

    # ===== 后面是功能性方法-》提供具体数据
    # 处理数据库层面的注册功能
    def register(self, name, passwd) -> bool:
        sql = "select name from user where name=%s;"
        self.cur.execute(sql, [name])
        r = self.cur.fetchone()  # 能否查询到
        # 如果查询有这个那么 则不能注册
        if r:
            return False
        # 插入操作
        sql = "insert into user (name,passwd) values (%s,%s);"
        try:
            self.cur.execute(sql, [name, passwd])
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            self.db.rollback()
            return False

    # 登录
    def log_in(self, name, passwd) -> bool:
        # binary 让查询区分大小写
        sql = "select name,passwd from user where binary name=%s and binary passwd=%s;"
        self.cur.execute(sql, [name, passwd])
        r = self.cur.fetchone()  # 能否查询到
        if r:
            return True
        else:
            return False

    # 添加历史记录
    def add_history_log(self, name, word):
        sql = "select uid from user where  name=%s;"
        self.cur.execute(sql, [name])
        # fetchone读取到返回元组(uid, )否则返回None
        user_id = self.cur.fetchone()[0]
        # 向历史记录中插入name,user_id
        sql = "insert into his(word, user_id) values(%s, %s);"
        try:
            self.cur.execute(sql, [word, user_id])
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()

    # 查找单词
    def find_word(self, word):
        sql = "select mean from words where word=%s;"
        self.cur.execute(sql, [word])
        # 找到返回(mean,)没有返回None
        mean = self.cur.fetchone()
        if mean:
            return mean[0]

    # 查看历史记录
    def view_history_log(self, name):
        # name word time,只查取前10条
        sql = "select name, word, time from user left join his on user.uid=his.user_id \
              where name=%s order by time desc limit 10;"
        self.cur.execute(sql, [name])
        # 返回元组,没值则返回空元组
        return self.cur.fetchall()


