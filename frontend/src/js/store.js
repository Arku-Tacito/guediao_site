//全局变量
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {//全局变量
        login_flag: null,
        token_key: null
    },
    getters: {//get方法
        isLogin: state =>  {
            if (state.login_flag == "true") {
                return true;
            }
            return false;
        },
        getKey: state => {
            return state.token_key;
        }
    },
    mutations: {//set方法
        init: state => {
            let flag = window.sessionStorage.getItem("login_flag");
            if (flag == "true") {
                state.login_flag = flag;
            } else {
                state.login_flag = null;
            }
            let key = window.sessionStorage.getItem("token_key");
            if (key) {
                state.token_key = key;
            } else {
                state.token_key = null;
            }
        },
        setTokenkey: (state, key) => {
            state.token_key = key;
            window.sessionStorage.setItem("token_key", key);
        }
    },
    actions: {

    },
    modules: {

    }
})