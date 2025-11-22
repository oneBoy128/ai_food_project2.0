<template>
  <div>
    <div id="bgConter">
        <div class="box" id="blackBox">Indo</div>
        <div class="box" style="color:#ffffff" id="whiteBox">or Style</div>
    </div>
    <div class="conters">
        <div class="wow animate__animated animate__fadeInUp animate__slow" id="textTitle">
            悠闲大床房
        </div>
        <div class="text">
            <p class="wow animate__animated animate__fadeInUp animate__slow">悠闲大床房面积为150平方米, 设计装潢豪华舒适</p>
            <p class="wow animate__animated animate__fadeInUp animate__slow">独特双面软硬设计的床垫，多款功能性睡枕，独立的浴缸及热带雨林淋浴区，免费有线及无线宽带上网服务，让您的旅行更加舒适便捷。</p>
        </div>
        <div id="imgs" class="wow animate__animated animate__fadeInUp animate__slow">
            <el-carousel :interval="2000" height="560px" indicator-position="outside">
                <el-carousel-item label="">
                    <img src="../../../public/imgs/cityRoom.png">
                </el-carousel-item>
                <el-carousel-item >
                    <img src="../../../public/imgs/the_bathroom.jpg">
                </el-carousel-item>
            </el-carousel>
        </div>
        <div style="width:100%;height: 60px; position: relative; left: 0; right: 0; margin: 0 auto;margin-bottom: 117px; border-bottom: 1px solid #cacaca;"></div>
        <div class="wow animate__animated animate__fadeInUp animate__slow" id="textTitle">
            太子居室
        </div>
        <div class="text">
            <p class="wow animate__animated animate__fadeInUp animate__slow">太子居室面积为350平方米, 设计装潢豪华大气</p>
            <p class="wow animate__animated animate__fadeInUp animate__slow">这是一种根据需要专门设计的房间，每个房间都有卫生间。客房多台配备3080Ti电竞电脑，让你旅行中享受开黑的乐趣</p>
        </div>
        <div id="imgs" class="wow animate__animated animate__fadeInUp animate__slow">
            <el-carousel :interval="2000" height="560px" indicator-position="outside">
                <el-carousel-item>
                    <img src="../../../public/imgs/hotel_room.png">
                </el-carousel-item>
                <el-carousel-item >
                    <img src="../../../public/imgs/dianjin.jpg">
                </el-carousel-item>
            </el-carousel>
        </div>
        <div style="width:100%;height: 60px; position: relative; left: 0; right: 0; margin: 0 auto;margin-bottom: 117px; border-bottom: 1px solid #cacaca;"></div>
        <div class="wow animate__animated animate__fadeInUp animate__slow" id="textTitle">
          狗头之家
        </div>
        <div class="text">
            <p class="wow animate__animated animate__fadeInUp animate__slow">狗头之家面积为200平方米, 设计装潢奢华舒适</p>
            <p class="wow animate__animated animate__fadeInUp animate__slow">火星名师设计，赛博坦贵族血统。</p>
        </div>
        <div id="imgs" class="wow animate__animated animate__fadeInUp animate__slow">
            <el-carousel :interval="2000" height="560px" indicator-position="outside">
                <el-carousel-item>
                    <img src="../../../public/imgs/hotel_room2.jpg">
                </el-carousel-item>
                <el-carousel-item >
                    <img src="../../../public/imgs/nbroom.jpg">
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
    name:'IndoorPage',
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
        background: url('../../../public/imgs/indoor.png');
        background-size: 100% 100%;
        position: relative;
        top: -60px;
        left: 379px;
    }
    .box{
        font-size: 100px;
        position: relative;
        top: 296px;
        left: -218px;
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