<template>
  <div id="root">
    <router-view></router-view>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  // 关键：将axios请求放在组件的生命周期钩子或方法中
  data(){
    return{
      test_text:'123'
    }
  },
  methods: {
    // 封装请求为方法，可通过按钮触发
    testBackend() {
      axios({
        method: 'get',
        url: 'http://localhost:8081/test_connect', 
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
      }).then(resp => {
        console.log('后端请求成功：', resp.data) // 只打印核心数据
        this.test_text = resp.data
        console.log("测试",this.test_text)
      }).catch(err => {
        console.log('后端请求失败：', err.message) // 简化错误信息
      })
    }
  }
}
</script>

<style>
  *{
    padding: 0;
    margin: 0;
    text-decoration: none;
    list-style: none;
  }
  html{
    background-color: rgb(242, 242, 242);
  }
  body{
    overflow-x:hidden
  }
    ::-webkit-scrollbar
  {
      width:5px;
      height:5px;
      background-color:#F5F5F5;
  }
/*定义滚动条轨道
 内阴影+圆角*/
  ::-webkit-scrollbar-track
  {
      -webkit-box-shadow:inset 0 0 6px rgba(0,0,0,0.3);
      border-radius:10px;
      background-color:#F5F5F5;
  }
/*定义滑块
 内阴影+圆角*/
  ::-webkit-scrollbar-thumb
  {
      border-radius:10px;
      -webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3);
      background-color:#555;
  }
  
</style>
