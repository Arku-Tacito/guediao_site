# _*_ coding: utf-8 _*_
from flask import Flask, send_from_directory, jsonify, request, make_response
import os
from backend.config.config_interface import ConfigInterface

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Arku'

if __name__=="__main__":
    cfg = ConfigInterface()
    host = cfg.get(["host"])
    port = cfg.get(["port"])
    backend_path = cfg.get(["backend_path"])
    print(host, port)
    print(backend_path)
    app.run(host=host, port=port, debug=True)
