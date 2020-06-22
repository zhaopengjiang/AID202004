# **在线词典**
1. 需求分析

2. 技术分析
  * 用什么样的并发模型
  
        #Thread + IO多路复用
        采用进程完成(练习进程的使用)
  * 网络模型
  
        采用tcp 保证数据的可靠性
  * 两个界面怎么配合
  * 数据存储 --》 数据库
  
        数据库--》 dict
        数据表 ：  
            words  --> wid,word,mean
            user   --> uid,name,passwd
            history--> uid,word,time
        

3. 封装和结构设计

            m:模型 --> 数据处理模型数据库处理 根据服务端控制模型提出的需求操控数据
            v:视图 --> 数据展示视图   客户端模块
            c:控制 --> 逻辑处理控制  服务端并发模型： 接收请求，与客户端交互
        

4. 通信协议

        功能           协议   请求参数                  
        log in          L    name,passwd
        register        R    name,passwd
        find word       F    word,name
        history log     H    name
        exit            E
            
5. 功能模块设计

        框架搭建
        注册
            客户端 ：输入注册信息
                    发送注册请求 （注册信息）
                    等待反馈结果
                    Yes --> 注册成功
                    No --》 注册失败
        
            服务端 ： 接收请求信息
                     判断可否注册
                     将判断结果反馈给客户端
                     Yes ： 插入用户信息
                     No ： 结束
        登录
            查单词
                 客户端   输入单词
                 发送请求 （Q  name word）
                 得到结果 （单词解释或者查找不到）
    
            服务端   接收请求
                 查询单词
                 发送结果 （查到了，没查到都发送）
                 插入历史记录  name  word  time
        历史记录
        退出
6. 优化完善

        binary 区分大小写
        
