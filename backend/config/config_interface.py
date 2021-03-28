"""
@author: Arku Xu
@date: 2021-03-27 14:12:34
@Email: arku.xu@gmail.com
@brief: 配置读写接口
"""
# _*_ coding: utf-8 _*_
import os, sys
import json

get_line_cur = sys._getframe

def console_log(line=0, text=""):
    """""
    调试信息打印到控制台
    ------------
    @param: line 行数  text 自定义信息
    @return: 
    """""
    log_test = "[{}] line {}: {}".format(__name__, line, str(text))
    print(log_test)

class ConfigInterface:
    """""
    配置读写接口类
    -------------
    """""
    __json_data = None
    __path_dir = os.environ.get("CONFIGPATH")
    __max_depth = 5
    __filename = ""
    
    def __init__(self, filename="main_config.json"):
        """""
        初始化函数
        ------------
        @param: filename 配置文件名
        @return: 
        """""
        self.__filename = os.path.join(self.__path_dir ,filename)
    
    def __load__(self):
        """""
        加载json配置文件数据到缓存
        加载失败缓存会变成None
        ------------
        @return: 0成功 -1失败
        """""
        # 清空缓存
        self.__json_data = None 

        # 加载文件
        try:
            with open(self.__filename, 'r') as f:
                data = json.load(f)
                f.close()
        except Exception as e:
            console_log(get_line_cur().f_lineno, e)
            return -1
        self.__json_data = data
        return 0
    
    def __save__(self):
        """""
        保存缓存数据到json配置文件
        保存成功后会清空缓存
        ------------
        @param: 
        @return: 0成功 -1失败
        """""
        # 检查数据有效性
        if self.__json_data == None:
            console_log(get_line_cur().f_lineno, "No data.")
            return -1
        if type(self.__json_data) != dict:
            console_log(get_line_cur().f_lineno, "Wrong data type:{}.", type(self.__json_data))
            return -1
            
        # 写数据
        try:
            with open(self.__filename, 'w') as f:
                data = json.dumps(self.__json_data)
                f.write(data)
                f.close()
        except Exception as e:
            console_log(get_line_cur().f_lineno, e)
            return -1
        
        # 清空缓存
        self.__json_data = None
        return 0

    def get(self, key=None):
        """""
        获取json配置数据
        ------------
        @param: key 层次键名
        @return: 数据结果，出错返回None
        """""
        if type(key) != list:
            console_log(get_line_cur().f_lineno, "Invalid key type.")
            return None
        # 检查层次键最大深度
        if len(key) > self.__max_depth:
            console_log(get_line_cur().f_lineno, "Depth of json object is no more than {}.".format(self.__max_depth))
            return None

        # 读取配置文件
        ret = self.__load__()
        if ret != 0:
            console_log(get_line_cur().f_lineno, "Load data failed.")
            return None
        
        # 查找对象
        data = self.__json_data
        for uni in key:
            if type(data) != dict or uni not in data.keys():
                console_log(get_line_cur().f_lineno, "Data not found.")
                return None
            data = data[uni]
        return data

    def set(self, value, key=None):
        """""
        设置配置值
        ------------
        @param: value 设置值
        @param: key 层次键名
        @return: 0成功 -1失败
        """""
        if type(key) != list:
            console_log(get_line_cur().f_lineno, "Invalid key type.")
        # 检查层次键最大深度
        if len(key) > self.__max_depth:
            console_log(get_line_cur().f_lineno, "depth of json object is no more than {}".format(self.__max_depth))
            return -1
        max_len = len(key)

        #读取配置文件
        ret = self.__load__()
        if ret != 0:
            console_log(get_line_cur().f_lineno, "Load data failed.")
            return -1

        # 找到对象
        obj = {}
        val = self.__json_data
        for uni in key:
            if type(val) != dict or uni not in val.keys():
                console_log(get_line_cur().f_lineno, "Data not found.")
                return -1
            if obj == {}:
                obj = self.__json_data
            else:
                obj = val
            val = val[uni]
        obj[key[-1]] = value    # 赋值

        # 保存文件
        ret = self.__save__()
        if ret != 0:
            console_log(get_line_cur().f_lineno, "Save config {} failed.".format(self.__filename))
            return -1
        return 0
        


                
            
