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
export default {
    data(){
        return {
            user_name: "",
            passwd: "",
        }
    },
    methods:{
        tologin() {
            try {
                let user_name = this.user_name;
                let passwd = this.passwd;
                window.alert(user_name + passwd);
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