"""
@author: Arku Xu
@date: 2021-04-01 23:44:56
@Email: arku.xu@gmail.com
@brief: 初始化数据库脚本
"""
# _*_ coding: utf-8 _*_
from backend.config.configbase import ConfigBase, console_log, get_line_cur
from backend.modules.dbopr.dboprbase import DBoprBase
from backend.modules.cypher.cypherbase import CypherBase

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
        console_log(text="Getting ori_key failed.")
        return -1
    else:
        console_log(text="Getting ori_key: {}".format(orin_key))
        if len(orin_key) >=13:
            console_log(text="Warnning: The ori_key is too long(>=13) to generate different keys.")
    # 构造各种密钥并自身加密
    cypher = CypherBase(orin_key)
    account_activate_key = cypher.encrypt_AES(orin_key + "_act")   #激活账号的密钥
    user_important_key = cypher.encrypt_AES(orin_key + "_usr")  #用户安全数据密钥
    session_token_key = cypher.encrypt_AES(orin_key + "_tok")   #会话token密钥
    log_message_key = cypher.encrypt_AES(orin_key + "_log")     #日志安全数据密钥
    business_message_key = cypher.encrypt_AES(orin_key + "_bsn")    #业务安全数据密钥
    hash_salt = cypher.encrypt_AES(orin_key + "_slt")   #哈希盐值 
    
    console_log(text="Generate keys:\nact:{} usr:{} tok:{}\nlog:{} bsn:{} slt:{}".format(
        cypher.decrypt_AES(account_activate_key), 
        cypher.decrypt_AES(user_important_key),
        cypher.decrypt_AES(session_token_key),
        cypher.decrypt_AES(log_message_key),
        cypher.decrypt_AES(business_message_key),
        cypher.decrypt_AES(hash_salt)
    ))

    # 创建数据库，存储密钥
    dbopr = DBoprBase(dbname="shadow", dbtype=1)
    cl_sql = "drop table if exists Shadow"
    ret = dbopr.execute(cl_sql) #先删除原来的表
    if ret == None:
        return -1

    sql = "create table Shadow(\
            name char(32),\
            val  char(256));"
    ret = dbopr.execute(sql)
    if ret == None:
        return -1       

    shadows = {"activate": account_activate_key, "user": user_important_key,
            "seesion":  session_token_key, "log": log_message_key,
            "business": business_message_key, "salt": hash_salt}
    success = 0
    for uni in shadows.keys():
        sql = "insert into Shadow values('{}', '{}')".format(uni, shadows[uni])
        ret = dbopr.execute(sql)
        if ret == None:
            console_log(text="Insert key [{} : {}] failed.".format(uni, shadows[uni]))
        else:
            success += 1
    
    console_log(text="{} keys insert successfully.".format(success))
    
    sql = "select * from Shadow"
    ret = dbopr.execute(sql)
    if ret != None:
        console_log(text="{}".format(ret))
    return 0

def account_init():
    """""
    账号表创建
    ------------
    @param: 
    @return: 0成功 -1失败
    """""
    dbopr = DBoprBase("account", dbtype=1)
    cl_sql = "drop table if exists Account"
    ret = dbopr.execute(cl_sql)
    if ret == None:
        return -1
    
    sql = "create table Account(\
            user nchar(1024) unique,\
            nickname char(1024),\
            passwd char(2048),\
            email char(2048)\
            );"
    ret = dbopr.execute(sql)
    if ret == None:
        return -1
    else:
        console_log(text="Init table Account successfully.")
        return 0


if __name__ == "__main__":
    console_log(text="Init Database begin...")
    key_init()
    account_init()
