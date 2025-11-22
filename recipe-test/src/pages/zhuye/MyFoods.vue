<template>
  <div id="conter">
    <div id="canting" class="wow animate__animated animate__fadeInBottomRight animate__slow"></div>
    <div id="about">
        <div class="wow animate__animated animate__fadeInTopLeft" style="margin-bottom: 50px;">
            <p style="font-size: 5rem;font-weight: 300;">Meals</p>
            <p style="color: #898987;font-size: .875rem;line-height: 120%;">饮食</p>
        </div>
        <div class="wow animate__animated animate__fadeInBottomLeft animate__slow">
            <p>「智慧食谱 AI 助手」，是一场「动漫美学 × 智能料理」的奇妙碰撞！</p>
            <p>当软萌动漫风的美食精灵挥动魔法厨具</p>
            <p>50 万 + 份全球食谱便化作舌尖上的创意灵感，为你解锁从家常小炒到异域料理的美味方案。</p>
            <p>以 AI 大模型为核心驱动力，结合中式烹饪精髓与全球美食逻辑，不管你是厨房新手想快速上手家常菜，还是美食达人追求创意突破，它都能精准匹配你的口味偏好、食材储备甚至烹饪时长，秒出定制化食谱。</p>
            <p>更支持食材替换、营养分析、烹饪误区纠错等实用功能，让每一次下厨都轻松又有趣，小白也能变身次元料理大师～</p>
        </div>
    </div>
  </div>
</template>

<script>
export default {
    name:'MyFoods',
    data() {
        return {
            
        }
    },
}
</script>

<style scoped>
    #conter{
        width: 100%;
        height: 80vh;
        margin-top: 300px;
        display: flex;
        justify-content: space-evenly;
    }
    #about{
        width: 665px;
        height: 60%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    #about p{
        margin-bottom: 10px;
        color: #636361;
        font-size: 1rem;
    }
    #canting{
        width: 600px;
        height: 60%;
        margin-left: 126px;
        background: url('../../../public/imgs/ai_helper.png');
        background-size: 100% 100%;
    }
</style>