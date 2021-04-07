"""
@author: Arku Xu
@date: 2021-04-07 00:10:03
@Email: arku.xu@gmail.com
@brief: 基础邮件模块
"""
# _*_ coding: utf-8 _*_

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from backend.config.configbase import ConfigBase, console_log, get_line_cur

class MailBase:
    """""
    基础邮件类
    -------------
    
    """""
    # __sender_addr = ""
    # __sender_passwd = ""
    # __sender_name = ""
    # __server = ""
    # __port = 465
    # __timeout = 10
    
    def __init__(self, cfg_file="mail_config.json"):
        """""
        初始化配置
        ------------
        @param: cfg_file 配置文件
        @return: 
        """""
        # 获取配置
        cfgbase = ConfigBase(cfg_file)    #邮件配置文件
        self.__server = cfgbase.get(["smtp_server"])    #smtp服务器
        self.__sender_addr = cfgbase.get(["sender", "addr"])    #发送者邮箱
        self.__sender_passwd = cfgbase.get(["sender", "passwd"])    #发送者密钥
        self.__sender_name = cfgbase.get(["sender", "name"])    #发送者名称
        self.__port = cfgbase.get(["port"]) #发送端口
        self.__timeout = cfgbase.get(["timeout"])   #超时
        # 读取失败的默认值设置
        if self.__server == None:
            self.__server = ""
        if self.__sender_addr == None:
            self.__sender_addr = ""
        if self.__sender_passwd == None:
            self.__sender_passwd = ""
        if self.__sender_name == None:
            self.__sender_name = ""
        if self.__port == None:
            self.__port = 465
        if self.__timeout == None:
            self.__timeout = 10

    def get_cfg(self):
        """""
        获取邮件配置信息
        ------------
        @param: 
        @return: 返回邮件配置信息
        """""
        cfg = {}
        cfg["server"] = self.__server
        cfg["sender_addr"] = self.__sender_addr
        cfg["sender_passwd"] = self.__sender_passwd
        cfg["sender_name"] = self.__sender_name
        cfg["port"] = self.__port
        cfg["timeout"] = self.__timeout
        return cfg
    
    def send_text(self, title, text, to_addr, to_name=None):
        """""
        发送纯文本邮箱
        ------------
        @param: title   主题
        @param: text    文本内容
        @param: to_addr 收件人邮箱
        @param: to_name 收件人 
        @return: 0成功 -1失败
        """""
        # 设置邮箱实例
        msg = MIMEMultipart()
        msg['From'] = formataddr([self.__sender_name, self.__sender_addr])
        if type(to_name) != str:
            to_name = ""
        if type(to_addr) != str:
            to_addr = ""
        msg['To'] = formataddr([to_name, to_addr])
        msg['Subject'] = str(text)
        msg.attach(MIMEText(str(text), 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP_SSL(host=self.__server, port=self.__port, timeout=self.__timeout)
            server.login(self.__sender_addr, self.__sender_passwd)
            server.sendmail(self.__sender_addr, [to_addr,], msg.as_string())
            server.quit()
        
        except Exception as e:
            console_log(text=e)
            return -1
        
        console_log(text="Mail sent.")
        return 0

if __name__ == "__main__":
    mail_cfg = MailBase()
    print(mail_cfg.get_cfg())
    mail_cfg.send_text("问候邮件", "你好啊，我是虚空管家", "269316784@qq.com", "阿苦")

    