"""
@author: Arku Xu
@date: 2021-04-11 00:35:45
@Email: arku.xu@gmail.com
@brief: 用户相关定义
"""
# _*_ coding: utf-8 _*_

# 用户权限
NORIGHT = 0
SPECIAL_VISIT = 1
BUSINESS_MANAGE = 2
FILE_UP = 4
FILE_DOWN = 8
USER_MANAGE = 16

# 用户对象状态
NOUSED = 0
PASSENGER = 1
NOTAUTH = 2
ISAUTH = 3
ERROR = 4

# 认证结果状态码
SUCCESS = 0
FAILED = -1
INVALID_USER = -2
INVALID_PASSWD = -3
USER_EXIST = -4
USER_NOTEXIST = -5
EMAIL_EXIST = -6
EMAIL_NOTEXIST = -7
NICK_NAME_EXIST = -8
PASSWD_INCORRECT = -9
NO_RIGHT = -10
COOKIE_INCORRECT = -11
TIME_EXPIRED = -12
