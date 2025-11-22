import Vue from 'vue'
import App from './App.vue'
import store from './store/index'
import router from './router/index'
import VueRouter from 'vue-router'
import animate from 'animate.css'
import {WOW} from 'wowjs'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css';

Vue.config.productionTip = false
Vue.use(VueRouter)
Vue.use(animate)
Vue.use(ElementUI)
Vue.prototype.$wow = new WOW({
  live:false,
})

new Vue({
  render: h => h(App),
  store,
  router
}).$mount('#app')
