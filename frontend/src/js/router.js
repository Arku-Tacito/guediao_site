//页面路由
import Vue from 'vue'
import VueRouter from 'vue-router'
import NProgress from 'nprogress';

import { canGoPath } from "./const";
import store from './store'
import NOTFOUND_PAGE from "../views/404.vue"
import INDEX_PAGE from "../views/index.vue"
import LOGIN_PAGE from "../views/login.vue"
import SIGNUP_PAGE from "../views/signup.vue"

Vue.use(VueRouter)

const routes = [
	{
		path: '/',
		redirect: '/index'
	},
	{
		path: '/index',
		component: INDEX_PAGE
	},
	{
		path: '/login',
		component: LOGIN_PAGE
	},
	{
		path: '/signup',
		component: SIGNUP_PAGE
	},
	{
		path: "/404",
        component: NOTFOUND_PAGE
	},
	{
		path: "*",
		redirect: { path: '/404' }
	}
]

const router = new VueRouter({
	routes
});

router.beforeEach((to, from, next) => {
	NProgress.start();
	store.commit("init");//初始化登录状态
	if (canGoPath.indexOf(to.path) == -1) {//错误的路由
		let url = escape(to.fullPath);
		router.push("/404?redirect=" + url);		
	}
	else if (store.getters.isLogin) {//有登录的
		next();
	}
	else {//进入登录注册页面或404，就不跳转
		if (to.path == '/login' || to.path == '/404' || to.path == '/signup') {
			next();
		} else {//没登录，要跳转
			let url = escape(to.fullPath);
			router.push("/login?redirect=" + url);
		}
	}
});
router.afterEach((to,from) => {
	NProgress.done();
})

export default router