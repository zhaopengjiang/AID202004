# 创建数据存储表,准备工作
# 数据表 ：
# words --> wid, word, mean   单词表以前创建过就不重复创建了
# user --> uid, name, passwd
# history --> hid, word, time,user_id关联
import pymysql

# 建立数据库连接
db = pymysql.connect(host="localhost",
                     port=3306,
                     user="root",
                     password="123456",
                     database="dict",
                     charset="utf8")
cur = db.cursor()  # 创建游标对象
try:
    # sql = "create table user(uid int unsigned primary key auto_increment,\
    #                         name char(30) not null, passwd char(64) not null);"
    # cur.execute(sql)
    sql = "create table his(hid int unsigned primary key auto_increment,word varchar(30),\
          time datetime default now(), user_id int unsigned, constraint \
          user_fk foreign key(user_id) references user(uid) on delete \
          cascade on update cascade);"
    cur.execute(sql)
    db.commit()
except Exception as e:
    print(e)
    db.rollback()
cur.close()
db.close()
