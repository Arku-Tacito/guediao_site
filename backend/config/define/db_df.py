"""
@author: Arku Xu
@date: 2021-04-17 00:37:30
@Email: arku.xu@gmail.com
@brief: 数据库相关定义
"""
# _*_ coding: utf-8 _*_

# 数据库类型
TYPE_BUSINESS = 0
TYPE_ACCOUNT = 1
TYPE_LOG = 2

# 数据库_用户
DB_ACCOUNT = "account"
TABLE_ACCOUNT = "Account"
KEY_UID = "uid"
KEY_RID = "rid"
KEY_USER = "user"
KEY_NICKNAME = "nickname"
KEY_PASSWD = "passwd"
KEY_EMAIL = "email"

# 数据库_密钥
DB_SHADOW = "shadow"
TABLE_SHADOW = "Shadow"
KEY_KEYNAME = "name"
KEY_KEYVAL = "val"
ACTIVATE_KEYNAME = "activate"
USER_KEYNAME = "user"
TOKEN_KEYNAME = "token"
LOG_KEYNAME = "log"
BUSINESS_KEYNAME = "business"
SALT_KEYNAME = "salt"