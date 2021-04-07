"""
@author: Arku Xu
@date: 2021-03-29 01:00:22
@Email: arku.xu@gmail.com
@brief: 配置模块初始化脚本
"""
# _*_ coding: utf-8 _*_
from backend.config.configbase import ConfigBase
from backend.modules.logopr.logbase import LogBase
import os, sys

if __name__=="__main__":
    test_log = LogBase(__name__).config(level="info")
    test_log.debug("hey, debug")
    test_log.info("hey, info")
    test_log.critical("hey, critical")