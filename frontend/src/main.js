import Vue from 'vue'
import App from './App.vue'
import router from './js/router.js'
import store from "./js/store.js";

new Vue({
  router,
  store,
  el: '#app',
  render: h => h(App)
})
