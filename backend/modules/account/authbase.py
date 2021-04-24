"""
@author: Arku Xu
@date: 2021-04-09 00:35:50
@Email: arku.xu@gmail.com
@brief: 用户认证基础模块，账号，会话认证
"""
# _*_ coding: utf-8 _*_
import time
from backend.config.configbase import ConfigBase
from backend.config.define import auth_df, db_df
from backend.modules.dbopr.dboprbase import DBoprBase
from backend.modules.cypher.cypherbase import CypherBase
from backend.modules.logopr.logbase import Log

log = Log(__name__).config()

class AuthBase:
    """""
    用户认证模块
    -------------
    用户的注册、登录、权限识别
    """""
    def __init__(self):
        self.__salt = None                  #哈希盐值
        self.__activate_key = None          #激活密钥
        self.__usr_key = None               #用户重要信息密钥
        self.__token_key = None             #token密钥——与用户共享的
        self.__cyphor =  CypherBase()       #加密模块
        self.__usrdb = DBoprBase(dbname=db_df.DB_ACCOUNT, dbtype=db_df.TYPE_ACCOUNT)    #用户数据库
        self.__usrtable = db_df.TABLE_ACCOUNT
        self.__timeout = ConfigBase().get(["session", "timeout"])
        
        # 获取相关密钥
        db = DBoprBase(db_df.DB_SHADOW, dbtype=db_df.TYPE_ACCOUNT)
        ret = db.connet()
        if ret != 0:
            log.debug("connet to {} db failed.".format(db_df.DB_SHADOW))
            return
        sql = "select * from {}".format(db_df.TABLE_SHADOW)
        result = db.execute(sql)
        if result == None:
            log.debug("select key failed.")
            return
        db.close()
        
        for uni in result:
            if uni[0] == db_df.ACTIVATE_KEYNAME:
                self.__activate_key = uni[1]
                continue
            if uni[0] == db_df.USER_KEYNAME:
                self.__usr_key = uni[1]
                continue
            if uni[0] == db_df.TOKEN_KEYNAME:
                self.__token_key = uni[1]
                continue
            if uni[0] == db_df.SALT_KEYNAME:
                self.__salt = uni[1]
                continue
        
        log.debug("select key success.")
        return
    
    def __key_available(self):
        """""
        密钥是否可用
        ------------
        @param: 
        @return: True成功 False失败
        """""
        if (self.__activate_key == None or self.__usr_key == None
            or self.__token_key == None or self.__salt == None):
            return False
        
        return True
    
    def __isexist__(self, key, val):
        """""
        用户信息是否存在
        ------------
        @param: key     用户名/邮箱... 
        @param: val     对应值 
        @return: 1存在 0不存在 -1出错
        """""
        sql = "select * from {} where {}=?".format(self.__usrtable, key)
        tup = (val,)
        ret = self.__usrdb.execute(sql, tup)
        if ret == None:
            return -1
        if len(ret) == 0:
            return 0
        return 1

    def print_key(self):
        log.debug("keys:\nactivate:{}\nuser:{}\ntoken:{}\nsalt:{}"
                    .format(self.__activate_key, self.__usr_key, self.__token_key, self.__salt))
    
    def print_user(self):
        self.__usrdb.connet()
        sql = "select * from {}".format(self.__usrtable)
        ret = self.__usrdb.execute(sql)
        print(ret)

    def get_activate_key(self):
        return self.__activate_key

    def get_token_key(self):
        return self.__token_key
    
    def get_hash_salt(self):
        return self.__salt
    
    def get_usr_key(self):
        return self.__usr_key
    
    def sign_up(self, usrinfo):
        """""
        用户注册
        ------------
        @param: usrinfo 注册信息，必须与表键名一一对应
        @return: 0成功 other错误
        """""
        if not self.__key_available():
            log.debug("keys are invailable.")
            return auth_df.FAILED
        if type(usrinfo) != dict:
            log.debug("usrinfo must be a dict.")
            return auth_df.FAILED

        # 开启数据库连接
        ret = self.__usrdb.connet()
        if ret != 0:
            log.debug("connetion failed.")
            return auth_df.FAILED

        # 提取用户信息
        if usrinfo[db_df.KEY_USER] == None:     #用户名
            log.debug("no usrname.")
            self.__usrdb.close()
            return auth_df.FAILED
        else:
            exist_ret = self.__isexist__(db_df.KEY_USER, usrinfo[db_df.KEY_USER])
            if exist_ret == -1:
                log.debug("unkwon failed.")
                self.__usrdb.close()
                return auth_df.FAILED
            if exist_ret == 1:
                log.debug("user is exist.") #用户名存在
                self.__usrdb.close()
                return auth_df.USER_EXIST
        if usrinfo[db_df.KEY_EMAIL] == None:    #邮箱
            log.debug("no email.")
            self.__usrdb.close()
            return auth_df.FAILED
        else:
            email = self.__cyphor.encrypt_AES(text=usrinfo[db_df.KEY_EMAIL], key=self.__usr_key)    #邮箱加密
            if email == None:
                log.debug("encrypt email failed.")
                self.__usrdb.close()
                return auth_df.FAILED
            exist_ret = self.__isexist__(db_df.KEY_EMAIL, email)
            if exist_ret == -1:
                log.debug("unkwon failed.")
                self.__usrdb.close()
                return auth_df.FAILED
            if exist_ret == 1:
                log.debug("email is exist.")    #邮箱存在
                self.__usrdb.close()
                return auth_df.EMAIL_EXIST
        if usrinfo[db_df.KEY_PASSWD] == None:   #密码
            log.debug("no passwd")
            self.__usrdb.close()
            return auth_df.FAILED
        
        # 加密信息
        passwd = self.__cyphor.hash(text=usrinfo[db_df.KEY_PASSWD], salt=self.__salt)   #密钥直接哈希
        if passwd == None:
            log.debug("hash passwd failed.")
            self.__usrdb.close()
            return auth_df.FAILED
        
        # 写入数据库
        sql = "insert into {}({}, {}, {}, {}, {}) values({}, '{}', '{}', '{}', '{}')".format(
                self.__usrtable, db_df.KEY_RID, db_df.KEY_USER, db_df.KEY_NICKNAME, db_df.KEY_PASSWD, db_df.KEY_EMAIL, 
                0, usrinfo[db_df.KEY_USER], usrinfo[db_df.KEY_NICKNAME], passwd, email)
        ret = self.__usrdb.execute(sql)
        if ret == None:
            log.debug("insert user failed.")
            self.__usrdb.close()
            return auth_df.FAILED
        
        # 成功关闭连接
        self.__usrdb.close()
        return auth_df.SUCCESS
    
    def log_in(self, user, passwd):
        """""
        用户登录
        ------------
        @param: user    用户名
        @param: passwd  密码，哈希过的
        @return: 0成功 other错误
        """""
        if user == None:
            log.debug("user is none")
            return auth_df.FAILED
        if passwd == None:
            log.debug("passwd is none.")
            return auth_df.FAILED
        if not self.__key_available():
            log.debug("keys are invailable.")
            return auth_df.FAILED
        
        # 创建连接
        ret = self.__usrdb.connet()
        if ret != 0:
            log.debug("connet to {} failed.".format(db_df.DB_ACCOUNT))
            return auth_df.FAILED
        
        # 构造查询语句
        sql = "select {} from {} where {} = ?".format(
            db_df.KEY_PASSWD, db_df.TABLE_ACCOUNT, db_df.KEY_USER)
        ret = self.__usrdb.execute(sql, (user,))
        
        # 结果检查
        if ret == None:
            log.debug("select failed.")
            self.__usrdb.close()
            return auth_df.FAILED
        if len(ret) == 0:   #用户名不存在
            log.debug("user {} not found.".format(user))
            self.__usrdb.close()
            return auth_df.USER_NOTEXIST
        
        result_passwd = ret[0][0]
        passwd = self.__cyphor.hash(passwd, self.__salt)    # 密码哈希
        if result_passwd != passwd: #密码错误
            log.debug("passwd incorrect.")
            self.__usrdb.close()
            return auth_df.PASSWD_INCORRECT
        
        # 断开连接，返回
        self.__usrdb.close()
        return auth_df.SUCCESS
        
    def get_user_ticket(self, user, ip='0.0.0.0'):
        """
        生成并获取用户ticket(必须得用户登录后才能用)
        ticket = E[usr_key](time) + hash(E[usr_key](user) + ip)
        ------------
        @param: user 用户名
        @param: ip  用户ip
        @return:    成功返回ticket 失败返回None
        """
        if user == None:
            log.debug("user is none")
            return None
        if not self.__key_available():
            log.debug("keys are invailable.")
            return None
        
        # 获取时间
        thistime = str(int(time.time()))
        en_time = self.__cyphor.encrypt_AES(thistime, key=self.__usr_key)
        en_usr = self.__cyphor.encrypt_AES(user, key=self.__usr_key)
        hash_usr = self.__cyphor.hash(en_usr + ip, salt=self.__salt)
        if en_time == None or hash_usr == None:
            log.debug("encrypt failed.")
            return None
        
        return en_time + hash_usr

    def auth_user_ticket(self, user, ticket, ip='0.0.0.0'):
        """
        ticket认证
        ------------
        @param: user    用户名
        @param: ticket  凭证
        @param: ip      用户ip
        @return: 0成功 other失败
        """
        if user == None:
            log.debug("user is none.")
            return auth_df.FAILED
        if ticket == None:
            log.debug("ticket is none.")
            return auth_df.FAILED
        if not self.__key_available():
            log.debug("keys are invailable.")
            return auth_df.FAILED
        
        # 拆解ticket
        sum_len = len(ticket)   #ticket总长
        en_usr = self.__cyphor.encrypt_AES(user, key=self.__usr_key)
        hash_usr = self.__cyphor.hash(en_usr + ip, salt=self.__salt)
        usr_len = len(hash_usr) #ticket中user部分长度

        time_part = ticket[:sum_len - usr_len]  #时间部分
        usr_part = ticket[sum_len - usr_len:]   #用户部分
        log.debug("time_part:{}\nusr:{}".format(time_part, usr_part))

        # 校验ticket
        if usr_part != hash_usr:    #用户部分错误
            log.debug("ticket invalid.")
            return auth_df.ticket_INCORRECT
        
        that_time = int(self.__cyphor.decrypt_AES(time_part, key=self.__usr_key))
        this_time = int(time.time())
        if that_time - this_time > self.__timeout:    #ticket过期
            log.debug("ticket is expired.")
            return auth_df.TIME_EXPIRED
        
        return auth_df.SUCCESS
        

if __name__ == "__main__": 
    auth = AuthBase()
    auth.print_key()

    # 注册
    usrinfo = {"user": "arku", "nickname": None, "passwd": "aa123", "email": "aaa@qq.com"}
    auth.sign_up(usrinfo)
    auth.print_user()

    # 登录
    ret = auth.log_in("arku", "aa123")
    if ret == 0:
        print("log in success.")
    else:
        print("log failed")

    # 获取token
    ret = auth.get_user_ticket("arku")
    print("ticket: {}".format(ret))

    ret = auth.auth_user_ticket("arku", ret)
    if ret == 0:
        print("ticket is corrected.")
    else:
        print("ticket is not corrected.")
