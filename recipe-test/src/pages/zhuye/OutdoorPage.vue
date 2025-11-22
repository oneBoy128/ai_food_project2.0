<template>
  <div>
    <div id="bgConter">
        <div class="box" id="blackBox">Outdo</div>
        <div class="box" style="color:#ffffff" id="whiteBox">or Style</div>
    </div>
    <div class="conters">
        <div class="wow animate__animated animate__fadeInUp animate__slow" id="textTitle">
            酒店布局
        </div>
        <div class="text">
            <p class="wow animate__animated animate__fadeInUp animate__slow">从豪华帐篷和酒店住宿到私人住宅，您可以根据自己的喜好进行定制。</p>
            <p class="wow animate__animated animate__fadeInUp animate__slow">酒店装饰使用赛博坦星最常用的盾牌座UY放射物，因此颜色变色和污垢较少，从长远来看，易于清洁。</p>
        </div>
        <div id="imgs" class="wow animate__animated animate__fadeInUp animate__slow">
            <el-carousel :interval="2000" height="560px" indicator-position="outside">
                <el-carousel-item>
                    <img src="../../../public/imgs/hotel.png">
                </el-carousel-item>
                <el-carousel-item >
                    <img src="../../../public/imgs/qiantai.jpg">
                </el-carousel-item>
                <el-carousel-item >
                    <img src="../../../public/imgs/swimming_pool.png">
                </el-carousel-item>
            </el-carousel>
        </div>
        <div style="width:100%;height: 60px; position: relative; left: 0; right: 0; margin: 0 auto;margin-bottom: 117px; border-bottom: 1px solid #cacaca;"></div>
    </div>
    <ContactUs/>
  </div>
</template>

<script>
import ContactUs from '@/components/ContactUs.vue';
export default {
    name:'OutdoorPage',
    data() {
        return {
            
        }
    },
    mounted(){
        this.$wow.init()
    },
    components:{
        ContactUs
    }
}
</script>

<style scoped>
    #bgConter{
        display: flex;
        width: 1192px;
        height: 656px;
        background: url('../../../public/imgs/outdoor.png');
        background-size: 100% 100%;
        position: relative;
        top: -60px;
        left: 379px;
    }
    .box{
        font-size: 100px;
        position: relative;
        top: 296px;
        left: -305px;
    }
    .conters{
        width: 1000px;
        padding: 0px 20px;
        position: relative;
        left: 0;
        right: 0;
        margin: 0 auto;
        margin-top: 186px;
    }
    #textTitle{
        font-size: 60px;
    }
    .text{
        width: 980px;
        margin-top: 30px;
        font-size: 20px;
        color: rgb(102, 102, 102);
    }
    .text p{
        padding-bottom: 20px;
    }
    #imgs{
        width: 100%;
        margin-top: 50px;
    }
    #imgs img{
        height: 100%;
        width: 100%;
    }
</style>