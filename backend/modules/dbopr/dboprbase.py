"""
@author: Arku Xu
@date: 2021-04-01 22:56:53
@Email: arku.xu@gmail.com
@brief: 数据库操作接口基类
"""
# _*_ coding: utf-8 _*_
import sqlite3
import os, sys
from backend.config.configbase import ConfigBase
from backend.modules.logopr.logbase import Log

log = Log(__name__).config()

class DBoprBase:
    """""
    规则库操作接口
    数据库类型：["business", "account", "log"]
    数据库的连接和关闭一般需要手动调用接口
    -------------
    setdb: 手动设置规则库名
    execute: 基础执行sql语句
    isexist: 表是否存在
    connet: 连接数据库
    close: 关闭连接
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
            log.debug("None database init.")
            return
        elif dbtype < 0 or dbtype >= len(self.__dbtype):
            log.debug("Invalid dbtype. Auto set type: 0")
            dbtype = 0
        path = os.path.join(os.getenv("DATAFIGPATH"), self.__dbtype[dbtype])
        self.__dbname = os.path.join(path, dbname)
    
    def __conn__(self):
        try:
            self.__dbconn = sqlite3.connect(self.__dbname)
        except Exception as e:
            log.debug(e)
            return -1
        
        if self.__dbconn != None:
            return 0
        else:
            log.debug("db connet is null.")
            return -1

    def __close__(self):
        if self.__dbconn == None:
            return 0

        try:    
            self.__dbconn.close()
            return 0
        except Exception as e:
            log.debug(e)
            return -1

    def setdb(self, dbname, dbtype=0):
        """""
        手动设置规则库名
        ------------
        @param: dbname  规则库名
        @return: 0成功 -1失败 
        """""
        if dbname == None:
            log.debug("None database init.")
            return -1
        elif len(dbtype) < 0 or len(dbtype) >= len(self.__dbtype):
            log.debug("Invalid dbtype. Auto set type: 0")
            dbtype = 0
        path = os.path.join(os.getenv("DATAFIGPATH"), self.__dbtype[dbtype])
        self.__dbname = os.path.join(path, dbname) 
        return 0

    def connet(self):
        """""
        连接数据库
        ------------
        @param: 
        @return: 0成功 -1失败
        """""
        ret = self.__conn__()
        return ret

    def close(self):
        """""
        关闭数据库
        ------------
        @param: 
        @return: 0成功 -1失败
        """""
        ret = self.__close__()
        return ret

    def execute(self, sql, vals=None):
        """""
        执行单条sql语句
        非安全函数
        ------------
        @param: sql     单条sql语句
        @param: vals    占位符下的值
        @return:        成功返回结果list(无结果则为空表)  失败返回None
        """""

        # 连接不正常，停止执行
        if self.__dbconn == None:
            log.debug("No connection to {} failed.".format(self.__dbname))
            return None
        
        # 执行sql语句
        cur = self.__dbconn.cursor()

        if type(sql) != str:
            log.debug("Sql have to be a str")
            return None
        try:
            if type(vals) != tuple:
                cur.execute(sql)
            else:
                cur.execute(sql, vals)
            self.__dbconn.commit()
        except Exception as e:
            log.debug(e)
            return None
        
        # 返回结果
        result = []
        for uni in cur:
            result.append(uni)
        return result
    
    def isexist(self, table):
        """""
        表是否存在
        ------------
        @param: table   表名
        @return: True 存在 False 不存在
        """""
        # 连接不正常，停止执行
        if self.__dbconn == None:
            log.debug("No connection to {} failed.".format(self.__dbname))
            return None

        if type(table) != str or table == "":
            log.debug("Invalid table name.")
            return False

        # 查找表
        sql = "SELECT count(*) FROM sqlite_master WHERE type=\"table\" AND name = ?"
        ret = self.execute(sql, (table,))
        if ret == None:
            return False
        elif ret[0][0] == 0:
            return False
        else:
            return True
        