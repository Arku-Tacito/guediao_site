# _*_ coding: utf-8 _*_
from flask import Flask, send_from_directory, jsonify, request, make_response
import os
from backend.config.configbase import ConfigBase

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Arku'

if __name__=="__main__":
    cfg = ConfigBase()
    host = cfg.get(["host"])
    port = cfg.get(["port"])
    print(host, port)
    # app.run(host=host, port=port, debug=True)
