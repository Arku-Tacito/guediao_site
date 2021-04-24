<template>
    <div id='signup'>
        <h1>
            注册账号
        </h1>
        <input v-model="user" placeholder="用户名"></input>
        <input v-model="passwd" placeholder="密码"></input>
        <input v-model="nickname" placeholder="昵称"></input>
        <input v-model="email" placeholder="邮箱"></input>
        <button @click="tosignup">注册</button>
        <button @click="back">返回</button>
    </div>
</template>

<script>
import { request } from '../js/request.js';
export default {
    data(){
        return{}
    },
    methods: {
        async tosignup(){
            //封装表单
            var data = {
                "data": {
                    "user": this.user,
                    "passwd": this.passwd,
                    "nickname": this.nickname,
                    "email": this.email
                }
            };
            try {
                let res = await request('/signup', 'post', data);//提交注册
                window.alert(res.data.msg);
                this.$router.push('/');//跳转
            } catch(error) {
                window.alert(error);
            }
        },
        back(){
            this.$router.push("/");
        }
    }
}
</script>