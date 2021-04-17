"""
@author: Arku Xu
@date: 2021-04-01 23:44:56
@Email: arku.xu@gmail.com
@brief: 初始化数据库脚本
"""
# _*_ coding: utf-8 _*_
from backend.config.configbase import ConfigBase
from backend.config.define import db_df
from backend.modules.dbopr.dboprbase import DBoprBase
from backend.modules.cypher.cypherbase import CypherBase
from backend.modules.logopr.logbase import Log

log = Log(__name__).config()

def key_init():
    """
    初始化密钥数据库
    ------------
    @param:
    @return: 0成功 -1失败
    """
    cfg = ConfigBase()
    
    # 获取原始密钥
    orin_key = cfg.get(["ori_key"])
    if orin_key == None:
        log.debug("Getting ori_key failed.")
        return -1
    else:
        log.debug("Getting ori_key: {}".format(orin_key))
        if len(orin_key) >=13:
            log.warning("Warnning: The ori_key is too long(>=13) to generate different keys.")
    # 构造各种密钥并自身加密
    cypher = CypherBase(orin_key)
    account_activate_key = cypher.encrypt_AES(orin_key + "_act")   #激活账号的密钥
    user_important_key = cypher.encrypt_AES(orin_key + "_usr")  #用户安全数据密钥
    session_token_key = cypher.encrypt_AES(orin_key + "_tok")   #会话token密钥
    log_message_key = cypher.encrypt_AES(orin_key + "_log")     #日志安全数据密钥
    business_message_key = cypher.encrypt_AES(orin_key + "_bsn")    #业务安全数据密钥
    hash_salt = cypher.encrypt_AES(orin_key + "_slt")   #哈希盐值 
    
    log.debug("Generate keys:\nact:{} usr:{} tok:{}\nlog:{} bsn:{} slt:{}".format(
        cypher.decrypt_AES(account_activate_key), 
        cypher.decrypt_AES(user_important_key),
        cypher.decrypt_AES(session_token_key),
        cypher.decrypt_AES(log_message_key),
        cypher.decrypt_AES(business_message_key),
        cypher.decrypt_AES(hash_salt)
    ))

    # 创建数据库，存储密钥
    dbopr = DBoprBase(dbname=db_df.DB_SHADOW, dbtype=db_df.TYPE_ACCOUNT)
    ret = dbopr.connet()    #连接数据库
    if ret != 0:
        log.debug("connet to db:{} failed".format(db_df.DB_SHADOW))
        return -1
    cl_sql = "drop table if exists {}".format(db_df.DB_SHADOW)
    ret = dbopr.execute(cl_sql) #先删除原来的表
    if ret == None:
        dbopr.close()
        return -1

    sql = "create table {}({} char(32),{}  char(256));".format(
        db_df.TABLE_SHADOW, db_df.KEY_KEYNAME, db_df.KEY_KEYVAL)
    ret = dbopr.execute(sql)
    if ret == None:
        dbopr.close()
        return -1       
    # 密钥要截断16位
    shadows = {db_df.ACTIVATE_KEYNAME: account_activate_key[:16], db_df.USER_KEYNAME: user_important_key[:16],
            db_df.TOKEN_KEYNAME:  session_token_key[:16], db_df.LOG_KEYNAME: log_message_key[:16],
            db_df.BUSINESS_KEYNAME: business_message_key[:16], db_df.SALT_KEYNAME: hash_salt}
    success = 0
    # 插入密钥
    for uni in shadows.keys():
        sql = "insert into {} values('{}', '{}')".format(db_df.TABLE_SHADOW, uni, shadows[uni])
        ret = dbopr.execute(sql)
        if ret == None:
            log.debug("Insert key [{} : {}] failed.".format(uni, shadows[uni]))
        else:
            success += 1
    
    log.debug("{} keys insert successfully.".format(success))
    
    sql = "select * from {}".format(db_df.TABLE_SHADOW)
    ret = dbopr.execute(sql)
    if ret != None:
        log.debug("{}".format(ret))
    
    dbopr.close()
    return 0

def account_init():
    """""
    账号表创建
    ------------
    @param: 
    @return: 0成功 -1失败
    """""
    dbopr = DBoprBase(db_df.DB_ACCOUNT, dbtype=db_df.TYPE_ACCOUNT)
    ret = dbopr.connet()    #连接数据库
    if ret != 0:
        log.debug("connet to db:{} failed".format(db_df.DB_ACCOUNT))
        return -1
    cl_sql = "drop table if exists {}".format(db_df.TABLE_ACCOUNT)
    ret = dbopr.execute(cl_sql)
    if ret == None:
        dbopr.close()
        return -1
    
    sql = "create table {}(\
            {} integer primary key autoincrement,\
            {} interger,\
            {} nchar(128) unique,\
            {} nchar(128),\
            {} char(256),\
            {} char(256)\
            );".format(db_df.TABLE_ACCOUNT, db_df.KEY_UID, db_df.KEY_RID,
                        db_df.KEY_USER, db_df.KEY_NICKNAME, db_df.KEY_PASSWD, db_df.KEY_EMAIL)
    ret = dbopr.execute(sql)
    if ret == None:
        dbopr.close()
        return -1
    else:
        log.debug("Init table {} successfully.".format(db_df.TABLE_ACCOUNT))
        dbopr.close()
        return 0


if __name__ == "__main__":
    log.debug("Init Database begin...")
    key_init()
    account_init()
