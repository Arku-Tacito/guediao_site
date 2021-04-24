import axios from 'axios';
import NProgress from 'nprogress'
import router from "./router.js"
import { baseUrl } from "./const.js";

export function request(url, type = 'get', data = {}, responseType = 'json') {
    NProgress.start();
    return new Promise((resolve, reject) => {
        axios({
            method: type,
            url,
            data: type == 'post' ? data : {},
            params: type == 'get' ? data : {},
            headers: {
                "Content-Type": "application/json;charset=UTF-8"
            },
            responseType
        }).then(res => {
            resolve(res);
            NProgress.done();
        }).catch(err => {
            reject(err)
            NProgress.done();
        })
    })
}

axios.interceptors.response.use(
    response => {
        // let conType = response.headers[ "Content-Type" ] || response.headers[ "content-type" ]
        let conType = response.headers[ "content-type" ]
        if (conType == "application/json;charset=UTF-8") {
            if (response.data.status == 'success') {
                return response.data;
            } else if (response.data.status == 'fail') {
                throw new Error(response.data.msg);
            } else if (response.data.status == 'nologin') {
                router.push("/login")
                throw new Error("请先登录您的账号");
            } else {
                return response.data;
                throw new Error("未知错误");
            }
        } else {
            return response
        }
    },
    error => {
        if (error.code == 'ECONNABORTED' && error.message.indexOf('timeout') != -1) {
            throw new Error("网络异常，请求超时");
        }
        if (!error.response || error.response.status == 500) {
            throw new Error("服务器异常");
        }
        throw new Error(error);
    }
)