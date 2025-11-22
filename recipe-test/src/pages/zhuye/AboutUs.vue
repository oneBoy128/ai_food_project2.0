<!-- 个人简介娱乐娱乐 -->
<template>
  <div id="yu_le" v-loading="loading">
    <div id="wby">
      <div class="jianjie animate__animated animate__rotateInDownRight">
        <h1 class="animate__animated animate__bounceInDown">
          制作者:<span style="margin-left: 69px">oneBoy</span>
        </h1>
        <h1 class="animate__animated animate__bounceInDown animate__slower">
          <br /><span
            >由 oneBoy 匠心打造，这是一场关于「AI +
            美食」的跨界实验。当柴犬宇航员身着宇航服，在星际间开启料理盲盒，每一份食谱都是大模型为你定制的宇宙级美味提案。
            从 0 到 1 搭建的大模型项目，以 50 万 +
            份全球食谱为基石，融合中式烹饪哲学与 AI
            创新思维，让你在地球厨房也能解锁「星际级料理」的惊喜。</span
          >
        </h1>
      </div>
      <div
        id="txwby"
        class="touxiang animate__animated animate__fadeInTopLeft"
      ></div>
    </div>
    <button @click="test">1</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AboutUs",
  data() {
    return {
      test_text: "",
      loading: false,
    };
  },
  methods: {
    test() {
      console.log("测试:", this.test_text);
      this.loading = true;
      axios
        .get("http://localhost:8081/test_connect")
        .then((resp) => {
          console.log("响应：", resp.data);
        })
        .catch((err) => {
          console.log("错误详情：", err.response || err);
        });
    },
  },
  mounted() {
    this.$wow.init();
  },
};
</script>

<style scoped>
#yu_le {
  margin-top: 30px;
  width: 100%;
  height: 80vh;
  padding-bottom: 30px;
}

#wby {
  width: 100%;
  height: 100%;
  background-image: linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%);
  display: flex;
  justify-content: space-between;
}
.touxiang {
  width: 350px;
  height: 350px;
  border-radius: 50%;
}
#txwby {
  position: relative;
  background: url(../../../public/imgs/doge4.png) no-repeat;
  background-size: 100% 100%;
  left: 24px;
  margin-right: 10%;
  margin-top: 170px;
}
h1 {
  position: relative;
  margin-top: 80px;
  margin-bottom: 90px;
}
.jianjie {
  position: relative;
  margin-left: 30px;
  width: 40%;
  height: 100%;
}
</style>
