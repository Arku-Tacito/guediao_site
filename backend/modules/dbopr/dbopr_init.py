"""
@author: Arku Xu
@date: 2021-04-01 23:44:56
@Email: arku.xu@gmail.com
@brief: 初始化数据库脚本
"""
# _*_ coding: utf-8 _*_
from backend.config.config_interface import ConfigInterface, console_log, get_line_cur
from backend.modules.dbopr.dbopr import DBOpr
from backend.modules.cypher.cypher_interface import Cypher

def KeyInit():
    """
    初始化密钥数据库
    ------------
    @param:
    @return: 0成功 -1失败
    """
    cfg = ConfigInterface()
    
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
    cypher = Cypher(orin_key)
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
    dbopr = DBOpr(dbname="shadow", dbtype=1)
    sql = "create table Shadow(\
            name char(32),\
            val  char(256));"
    ret = dbopr.execute(sql)
    if ret == None:
        # 可能表存在，删表见一次试试
        console_log(text="Table maybe existed already. Try to delete and create new one.")
        dl_sql = "drop table Shadow"
        ret = dbopr.execute(dl_sql)
        if ret == None:
            return -1
        else:
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
    return 0
        

if __name__ == "__main__":
    console_log(text="Init Database begin...")
    KeyInit()
