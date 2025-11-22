<template>
  <div id="conter">
    <div id="about">
        <div class="wow animate__animated animate__fadeInTopLeft" style="margin-bottom: 50px;">
            <p style="color:#898987;font-size:1rem;margin-bottom: 14px;">关于模型</p>
            <p style="color:#282823;font-size:2rem">the best food ai helper</p>
            <p style="color:#282823;font-size:2rem">一个十分优秀的ai helper</p>
        </div>
        <div class="wow animate__animated animate__fadeInBottomLeft animate__slow">
            <p>「智慧食谱 AI 助手」，是一场「动漫美学 × 智能料理」的奇妙碰撞！</p>
            <p>当软萌动漫风的美食精灵挥动魔法厨具</p>
            <p>50 万 + 份全球食谱便化作舌尖上的创意灵感，为你解锁从家常小炒到异域料理的美味方案。</p>
            <p>以 AI 大模型为核心驱动力，结合中式烹饪精髓与全球美食逻辑，它都能精准匹配你的口味偏好、食材储备甚至烹饪时长，秒出定制化食谱。</p>
            <p>更支持食材替换、营养分析、烹饪误区纠错等实用功能，让每一次下厨都轻松又有趣，小白也能变身次元料理大师～</p>
            <p></p>
        </div>
    </div>
    <div id="roomp" class="wow animate__animated animate__fadeInBottomRight animate__slow"></div>
  </div>
</template>

<script>
export default {
    name:'HistoryPage',
    data() {
        return {
            
        }
    },
    mounted() {
        this.$wow.init();
    },
}
</script>

<style scoped>
    #conter{
        position: relative;
        left: 0;
        right: 0;
        margin: 0 auto;
        width: 70%;
        height: 75%;
        margin-top: 10%;
        display: flex;
        justify-content: space-evenly;
        align-items: center;
    }
    #about{
        width: 60%;
        height: 100%;
    }
    #about p{
        margin-bottom: 10px;
        color: #636361;
        font-size: 1rem;
    }
    #roomp{
        width: 600px;
        height: 412.5px;
        margin-left: 15%;
        background: url(../../public/imgs/ai_helper2.png) no-repeat;
        background-size: 100% 100%;
    }
</style>