# _*_ coding: utf-8 _*_
from flask import Flask, send_from_directory, jsonify, request, make_response
import os, json
from datetime import datetime, timedelta
from backend.config.configbase import ConfigBase
from backend.modules.account.authbase import AuthBase
from backend.config.define import auth_df, db_df, sv_df

authbase = AuthBase()
cookie_timeout = ConfigBase().get(["cookie", "timout_days"])
app = Flask(__name__, static_folder='../frontend/', static_url_path="")

def auth_ticket():
    """""
    验证ticket
    如果验证不通过, 返回制作好的response
    ------------
    @param: 
    @return: ret 0成功 -1失败
    @return: resp response 成功则返回None
    """""
    # 获取cookie
    user = request.cookies.get("user")
    ticket = request.cookies.get("ticket")
    ip = request.remote_addr
    ret = authbase.auth_user_ticket(user, ticket, ip)
    if ret != auth_df.SUCCESS:
        resp = make_responese_msg(status="nologin", msg="ticket not correct.")
    else:
        resp = None
    
    return ret, resp

def make_responese_msg(data=None, status="failed", login_flag=False, token=None, msg="none"):
    """
    设置返回数据
    ------------
    @param: data    业务数据
    @param: status  业务处理结果
    @param: login_flag  登录成功标记
    @param: token   密钥
    @param: msg     附加信息 
    @return:    成功返回response 失败返回None
    """
    if data == None:
        data = {}
    result = dict()
    result["data"] = data
    result["status"] = status
    result["login_flag"] = "true" if login_flag else "false"
    if token != None:
        result["token_key"] = token
    result["msg"] = msg
    try:
        resp = make_response(json.dumps(result))
        resp.headers ['Content-Type'] = 'application/json;charset=UTF-8'
        return resp
    except Exception as e:
        result = {"status":"failed"}
        resp = make_response(json.dumps(result))
        return resp

def set_cookie(resp, user=None, ip="0.0.0.0"):
    """""
    在response上设置cookie
    ------------
    @param: resp response
    @param: user 用户名
    @param: ip
    @return: 
    """""
    if user == None:
        return resp

    # 获取对应的ticket
    ret = authbase.get_user_ticket(user, ip)
    if ret == None:
        return resp
    
    expires = datetime.now() + timedelta(days=int(cookie_timeout))  #有效天数
    
    resp.set_cookie("user", user, expires=expires, httponly=True)
    resp.set_cookie("ticket", ret, expires=expires, httponly=True)
    return resp

@app.route('/')
def root():
    return app.send_static_file("index.html")

@app.route('/index')
def index():
    # 验证ticket, 不通过直接返回response
    ret, resp = auth_ticket()
    if ret != auth_df.SUCCESS:
        return resp
    
    # 制作成功response
    resp = make_responese_msg(status="success", login_flag="true", msg="欢迎")
    return resp

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()['data']
    # 登录并检查结果
    try:
        user = data['user']
        passwd = data['passwd']
        ret = authbase.log_in(user, passwd)
    except Exception as e:
        print(e)
        resp = make_responese_msg(msg="服务端异常")
        return resp
    
    if ret == auth_df.PASSWD_INCORRECT:
        resp = make_responese_msg(msg="密码错误")
    elif ret == auth_df.USER_NOTEXIST:
        resp = make_responese_msg(msg="用户不存在")
    elif ret != auth_df.SUCCESS:
        resp = make_responese_msg(msg="登录异常")
    else:
        resp = make_responese_msg(status="success", login_flag=True, msg="登录成功")
        # 设置cookie
        ip = request.remote_addr
        resp = set_cookie(resp, user, ip)
        
    return resp

@app.route('/signup', methods=['POST'])
def signup():
    # 获取并处理表单
    userinfo = request.get_json()['data']
    
    # 注册并检查结果
    ret = authbase.sign_up(userinfo)
    if ret == auth_df.EMAIL_EXIST:
        resp = make_responese_msg(msg="邮箱已存在")
    elif ret == auth_df.USER_EXIST:
        resp = make_responese_msg(msg="用户名已存在")
    elif ret != auth_df.SUCCESS:
        resp = make_responese_msg(msg="未知错误")
    else:
        resp = make_responese_msg(status="success", msg="注册成功")
    
    return resp

if __name__=="__main__":
    cfg = ConfigBase()
    host = cfg.get(["host"])
    port = cfg.get(["port"])
    print(host, port)
    app.run(host=host, port=port, debug=True)
