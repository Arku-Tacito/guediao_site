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

class LogBase(logging.getLoggerClass()):
    """""
    日志基类
    -------------
    config: 配置日志参数，返回self
    """""
    def config(self, cfg_file="log_config.json", level="debug"):
        """""
        获取配置
        ------------
        @param: cfg_file 配置文件名
        @return: self
        """""
        log_cfg = ConfigBase(cfg_file)
        
        outfile = log_cfg.get(["outfile"])
        if outfile == None:
            outfile = "default.log"
        path = os.getenv("DATAFIGPATH")
        path = os.path.join(path, "log")
        outfile = os.path.join(path, outfile)
        
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
        
        logformat = logging.Formatter('%(asctime)s [%(levelname)s]%(filename)s line %(lineno)d: %(message)s')

        file_handler = logging.FileHandler(outfile)
        console_handler = logging.StreamHandler()
        file_handler.setFormatter(logformat)
        console_handler.setFormatter(logformat)

        self.addHandler(file_handler)
        self.addHandler(console_handler)

        return self
