<template>
  <div id="conter">
    <div id="contactImg">
      <img src="../../public/imgs/contactUs.jpg" alt="">
      <div id="contacttext">
        <div style="margin-top: 54px;">
          <p style="font-size:44px;color:#ffffff">现在开始</p>
          <p style="font-size:44px;color:#ffffff">使用食谱助手</p>
        </div>
        <p style="font-size:20px;color:#ffffff;height: 205px;line-height: 205px;margin-left: 235px;">我们将为你提供优质的服务</p>
        <router-link id="goto" to="/chatpage"><i class="el-icon-right"></i></router-link>
      </div>
    </div>
    <div id="footer">
      made by : one boy | 2025-11-7 | xiaokui-rag-agent
    </div>
  </div>
</template>

<script>
export default {

}
</script>

<style scoped>
  #conter{
    width: 100%;
    margin-top: 50px;
  }
  #contactImg{
    width: 100%;
    height: 205px;
    background-color: rgba(0,0,0,.4);
    position: relative;
    overflow: hidden;
  }
  #contactImg img{
    width: 100%;
    height: 100%;
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: -1;
    transition:all .6s;
  }
  #contactImg:hover img{
    transform: scale(1.1);
  }
  #contacttext{
    width: 1100px;
    height: 139px;
    position: relative;
    left: 0;
    right: 0;
    margin: 0 auto;
    display: flex;
  }
  #goto{
    width: 95px;
    height: 95px;
    line-height: 95px;
    text-align: center;
    color: rgb(202, 202, 202);
    border-radius: 50%;
    font-size: 40px;
    margin-top: 50px;
    margin-left: 217px;
    border: rgb(202, 202, 202) 1px solid;
    transition: all .6s;
  }
  #goto:hover{
    background-color: #FFFFFF;
    color: black;
  }
  #footer{
    width: 100%;
    height: 40px;
    line-height: 40px;
    text-align: center;
    padding: 16px 0px;
    background: #71807c;
    color: #ffffff;
    font-size: 20px;
  }
</style>