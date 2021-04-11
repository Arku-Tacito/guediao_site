"""
@author: Arku Xu
@date: 2021-04-09 00:35:50
@Email: arku.xu@gmail.com
@brief: 用户认证基础模块，账号，会话认证
"""
# _*_ coding: utf-8 _*_
import time
from backend.config.configbase import ConfigBase
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
        self.__token_key = None             #token密钥
        self.__cyphor =  CypherBase()       #加密模块
        self.__usrdb = DBoprBase(dbname="account", dbtype=1)    #用户数据库
        self.__usrtable = "Account"
        
        # 获取相关密钥
        db = DBoprBase("shadow", dbtype=1)
        ret = db.connet()
        if ret != 0:
            log.debug("connet to shadow db failed.")
            return
        sql = "select * from Shadow"
        result = db.execute(sql)
        if result == None:
            log.debug("select key failed.")
            return
        db.close()
        
        for uni in result:
            if uni[0] == "activate":
                self.__activate_key = uni[1]
                continue
            if uni[0] == "user":
                self.__usr_key = uni[1]
                continue
            if uni[0] == "token":
                self.__token_key = uni[1]
                continue
            if uni[0] == "salt":
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
    
    def sign_up(self, usrinfo):
        """""
        用户注册
        ------------
        @param: usrinfo 注册信息，必须与表键名一一对应
        @return: 0成功 -1其他错误 -2用户名非法 -3密码非法 
                -4用户名存在 -5用户昵称存在 -6用户邮箱存在
        """""
        if not self.__key_available():
            log.debug("keys are invailable.")
            return -1
        if type(usrinfo) != dict:
            log.debug("usrinfo must be a dict.")
            return -1

        # 开启数据库连接
        ret = self.__usrdb.connet()
        if ret != 0:
            log.debug("connetion failed.")
            return -1

        # 提取用户信息
        if usrinfo["user"] == None:     #用户名
            log.debug("no usrname.")
            self.__usrdb.close()
            return -1
        else:
            exist_ret = self.__isexist__("user", usrinfo["user"])
            if exist_ret == -1:
                log.debug("unkwon failed.")
                self.__usrdb.close()
                return -1
            if exist_ret == 1:
                log.debug("user is exist.")
                self.__usrdb.close()
                return -4
        if usrinfo["email"] == None:    #邮箱
            log.debug("no email.")
            self.__usrdb.close()
            return -1
        else:
            exist_ret = self.__isexist__("email", usrinfo["email"])
            if exist_ret == -1:
                log.debug("unkwon failed.")
                self.__usrdb.close()
                return -1
            if exist_ret == 1:
                log.debug("email is exist.")
                self.__usrdb.close()
                return -6
        if usrinfo["passwd"] == None:   #密码
            log.debug("no passwd")
            self.__usrdb.close()
            return -1
        
        # 加密信息
        passwd = self.__cyphor.hash(text=usrinfo["passwd"], salt=self.__salt)   #密钥直接哈希
        if passwd == None:
            log.debug("hash passwd failed.")
            self.__usrdb.close()
            return -1
        email = self.__cyphor.encrypt_AES(text=usrinfo["email"], key=self.__usr_key)    #邮箱加密
        if email == None:
            log.debug("encrypt email failed.")
            self.__usrdb.close()
            return -1
        
        # 写入数据库
        sql = "insert into {}(rid, user, nickname, passwd, email) values({}, '{}', '{}', '{}', '{}')".format(
                self.__usrtable, 0, usrinfo['user'], usrinfo['nickname'], passwd, email)
        ret = self.__usrdb.execute(sql)
        if ret == None:
            log.debug("insert user failed.")
            self.__usrdb.close()
            return -1
        
        # 成功关闭连接
        self.__usrdb.close()
        return 0
        
        

if __name__ == "__main__": 
    auth = AuthBase()
    auth.print_key()

    usrinfo = {"user": "arku", "nickname": None, "passwd": "aa123", "email": "aaa@qq.com"}
    auth.sign_up(usrinfo)
    

    auth.print_user()

