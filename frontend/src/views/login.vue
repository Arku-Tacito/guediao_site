<template>
    <div id='login'>
        <h1>
            欢迎登录
        </h1>
            <input v-model="user_name" placeholder="输入用户名">
            <input v-model="passwd" placeholder="输入密码">
            <button @click="tologin">登录</button>
            <button @click="toregist">注册</button>
    </div>
</template>

<script>
import { request } from '../js/request.js';
export default {
    data(){
        return {
        }
    },
    methods:{
        async tologin() {
            //封装表单
            var data = {
                "data": {
                    "user": this.user_name,
                    "passwd": this.passwd
                }
            };
            try {
                let res = await request('/login', 'post', data);//登录
                window.alert(res.msg);
                this.$router.push('/index');
            } catch(error) {
                window.alert(error);
            }
        },
        toregist(){
            this.$router.push('/signup');
        }
    }
}
</script>