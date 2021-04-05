"""
@author: Arku Xu
@date: 2021-04-01 22:56:53
@Email: arku.xu@gmail.com
@brief: 基础数据库操作接口
"""
# _*_ coding: utf-8 _*_
import sqlite3
import os, sys
from backend.config.config_interface import ConfigInterface, console_log, get_line_cur

class DBOpr:
    """""
    规则库操作接口
    -------------
    setdb: 手动设置规则库名
    execute: 基础执行sql语句
    """""
    __dbname = ""   # 数据库文件
    __dbconn = None # 数据连接
    __dbtype = ["business", "account", "log"]
    
    def __init__(self, dbname=None, dbtype=0):
        """""
        初始化函数
        ------------
        @param: dbname  数据库名
        @param: dbtype  数据库类型
        @return: 
        """""
        if dbname == None:
            console_log(get_line_cur().f_lineno, "None database init.")
            return
        elif dbtype < 0 or dbtype >= len(self.__dbtype):
            console_log(get_line_cur().f_lineno, "Invalid dbtype. Auto set type: 0")
            dbtype = 0
        path = os.path.join(os.getenv("DATAFIGPATH"), self.__dbtype[dbtype])
        self.__dbname = os.path.join(path, dbname)
    
    def __conn__(self):
        try:
            self.__dbconn = sqlite3.connect(self.__dbname)
        except Exception as e:
            console_log(get_line_cur().f_lineno, e)

    def __close__(self):
        if self.__dbconn != None:
            self.__dbconn.close()
            return

    def setdb(self, dbname, dbtype=0):
        """""
        手动设置规则库名
        ------------
        @param: dbname  规则库名
        @return: 0成功 -1失败 
        """""
        if dbname == None:
            console_log(get_line_cur().f_lineno, "None database init.")
            return -1
        elif len(dbtype) < 0 or len(dbtype) >= len(self.__dbtype):
            console_log(get_line_cur().f_lineno, "Invalid dbtype. Auto set type: 0")
            dbtype = 0
        path = os.path.join(os.getenv("DATAFIGPATH"), self.__dbtype[dbtype])
        self.__dbname = os.path.join(path, dbname) 
        return 0

    def execute(self, sql=None):
        """""
        基础执行sql语句
        非安全函数
        ------------
        @param: sql     sql语句
        @return:        成功返回结果 失败返回None
        """""
        # 建立连接
        self.__conn__()
        if self.__dbconn == None:
            console_log(get_line_cur().f_lineno, "Connet to {} failed.".format(self.__dbname))
            return None
        cur = self.__dbconn.cursor()

        # 执行sql语句
        if type(sql) != str:
            console_log(get_line_cur().f_lineno, "Sql must be a string.")
            self.__close__()
            return None
        try:
            cur.execute(sql)
            self.__close__()
            return cur
        except Exception as e:
            console_log(get_line_cur().f_lineno, e)
            self.__close__()
            return None
