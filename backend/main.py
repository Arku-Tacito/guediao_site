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

def make_responese_msg(data=None, status="failed", msg="none"):
    """
    设置返回数据
    ------------
    @param: data    业务数据
    @param: status  业务处理结果
    @param: msg     附加信息 
    @return:    成功返回response 失败返回None
    """
    if data == None:
        data = "none"
    result = dict()
    result["data"] = data
    result["status"] = status
    result["msg"] = msg
    try:
        resp = make_response(json.dumps(result))
        resp.headers ['Content-Type'] = 'application/json;charset=UTF-8'
        return resp
    except Exception as e:
        result = {"status":"failed"}
        resp = make_response(json.dumps(result))
        return resp

def set_cookie(resp, user=None):
    """""
    在response上设置cookie
    ------------
    @param: user 用户名
    @return: 
    """""
    if user == None:
        return resp

    # 获取对应的ticket
    ret = authbase.get_user_ticket(user)
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
    resp = make_responese_msg()
    resp = set_cookie(resp, "arku")
    return resp

@app.route('/login')
def login():
    # 获取cookie
    user = request.cookies.get("user")
    ticket = request.cookies.get("ticket")
    ret = authbase.auth_user_ticket(user, ticket)
    if ret == auth_df.FAILED:
        resp = make_responese_msg(msg="ticket not correct.")
    else:
        resp = make_responese_msg(status="success", msg="ticket correct")
    
    return resp

if __name__=="__main__":
    cfg = ConfigBase()
    host = cfg.get(["host"])
    port = cfg.get(["port"])
    print(host, port)
    app.run(host=host, port=port, debug=True)
