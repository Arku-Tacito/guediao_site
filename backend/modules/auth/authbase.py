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
        self.__token_key = None             #token密钥
        self.__cyphor =  CypherBase()       #加密模块
        self.__usrdb = DBoprBase(dbname=db_df.DB_ACCOUNT, dbtype=db_df.TYPE_ACCOUNT)    #用户数据库
        self.__usrtable = db_df.TABLE_ACCOUNT
        
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
        if usrinfo["user"] == None:     #用户名
            log.debug("no usrname.")
            self.__usrdb.close()
            return auth_df.FAILED
        else:
            exist_ret = self.__isexist__("user", usrinfo["user"])
            if exist_ret == -1:
                log.debug("unkwon failed.")
                self.__usrdb.close()
                return auth_df.FAILED
            if exist_ret == 1:
                log.debug("user is exist.") #用户名存在
                self.__usrdb.close()
                return auth_df.USER_EXIST
        if usrinfo["email"] == None:    #邮箱
            log.debug("no email.")
            self.__usrdb.close()
            return auth_df.FAILED
        else:
            exist_ret = self.__isexist__("email", usrinfo["email"])
            if exist_ret == -1:
                log.debug("unkwon failed.")
                self.__usrdb.close()
                return auth_df.FAILED
            if exist_ret == 1:
                log.debug("email is exist.")    #邮箱存在
                self.__usrdb.close()
                return auth_df.EMAIL_EXIST
        if usrinfo["passwd"] == None:   #密码
            log.debug("no passwd")
            self.__usrdb.close()
            return auth_df.FAILED
        
        # 加密信息
        passwd = self.__cyphor.hash(text=usrinfo["passwd"], salt=self.__salt)   #密钥直接哈希
        if passwd == None:
            log.debug("hash passwd failed.")
            self.__usrdb.close()
            return auth_df.FAILED
        email = self.__cyphor.encrypt_AES(text=usrinfo["email"], key=self.__usr_key)    #邮箱加密
        if email == None:
            log.debug("encrypt email failed.")
            self.__usrdb.close()
            return auth_df.FAILED
        
        # 写入数据库
        sql = "insert into {}(rid, user, nickname, passwd, email) values({}, '{}', '{}', '{}', '{}')".format(
                self.__usrtable, 0, usrinfo['user'], usrinfo['nickname'], passwd, email)
        ret = self.__usrdb.execute(sql)
        if ret == None:
            log.debug("insert user failed.")
            self.__usrdb.close()
            return auth_df.FAILED
        
        # 成功关闭连接
        self.__usrdb.close()
        return auth_df.SUCCESS
    
    def sign_in(self, user, passwd):
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
            return auth_df.FAILED
        if len(ret) == 0:   #用户名不存在
            log.debug("user {} not found.".format(user))
            return auth_df.USER_NOTEXIST
        result_passwd = ret[0][0]
        if result_passwd != passwd: #密码错误
            log.debug("passwd incorrect.")
            return auth_df.PASSWD_INCORRECT
        
        # 断开连接，返回
        self.__usrdb.close()
        return auth_df.SUCCESS
        

        
        

if __name__ == "__main__": 
    auth = AuthBase()
    auth.print_key()

    # 注册
    usrinfo = {"user": "arku", "nickname": None, "passwd": "aa123", "email": "aaa@qq.com"}
    auth.sign_up(usrinfo)
    auth.print_user()

    # 登录
    salt = "I0k3i0ustmU4CcOe98/0Gw=="
    cypor = CypherBase()
    passwd = cypor.hash("aa123", salt)
    ret = auth.sign_in("arku", passwd)
    if ret == 0:
        print("log in success.")
    else:
        print("log failed")

