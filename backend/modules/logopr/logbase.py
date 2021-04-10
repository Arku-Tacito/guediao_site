"""
@author: Arku Xu
@date: 2021-04-07 22:19:08
@Email: arku.xu@gmail.com
@brief: 日志模块基类
"""
# _*_ coding: utf-8 _*_
import logging
import os
from logging.handlers import RotatingFileHandler
from backend.config.configbase import ConfigBase, console_log, get_line_cur

class Log(logging.getLoggerClass()):
    """""
    日志基类
    -------------
    config: 配置日志参数，返回self
    """""
    def config(self, cfg_file="log_config.json", level="global", mod='c'):
        """""
        获取配置
        ------------
        @param: cfg_file 配置文件名
        @level: 日志等级 默认global，从配置文件中获取
        @mod：  日志输出模式 f文件，c控制端
        @return: self
        """""
        log_cfg = ConfigBase(cfg_file)
        # 读取配置，设置输出文件路径
        outfile = log_cfg.get(["outfile"])
        if outfile == None:
            outfile = "default.log"
        path = os.getenv("DATAFIGPATH")
        path = os.path.join(path, "log")
        outfile = os.path.join(path, outfile)

        # 设置日志等级
        global_level = log_cfg.get(["global_loglevel"])
        if level == "global":
            level = global_level
        if level == "info":
            self.setLevel(logging.INFO)
        elif level == "warning":
            self.setLevel(logging.WARNING)
        elif level == "error":
            self.setLevel(logging.ERROR)
        elif level == "critical":
            self.setLevel(logging.CRITICAL)
        else:
            self.setLevel(logging.DEBUG)

        # 设置日志输出模式
        logformat = logging.Formatter('%(asctime)s [%(levelname)s]%(filename)s line %(lineno)d: %(message)s')

        if 'f' in mod:
            file_handler = logging.FileHandler(outfile)
            file_handler.setFormatter(logformat)
            self.addHandler(file_handler)
        if 'c' in mod:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logformat)
            self.addHandler(console_handler)

        return self