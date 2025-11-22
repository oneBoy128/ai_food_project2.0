<template>
  <div id="conter">
    <div class="wow animate__animated animate__fadeInUpBig" style="position: relative;left: 76px;margin-bottom: 10px;">
        <p style="font-size: 5rem;font-weight: 300;">Features</p>
        <p style="color: #898987;font-size: .875rem;line-height: 120%;">特征</p>
    </div>
    <div class="wow animate__animated animate__fadeInUp animate__delay-1s" id="gallery">
        <el-carousel :interval="2000" type="card" height="500px">
            <el-carousel-item>
                <img src="../../public/imgs/ai_feature1.png">
            </el-carousel-item>
            <el-carousel-item>
                <img src="../../public/imgs/ai_feature2.png">
            </el-carousel-item>
            <el-carousel-item>
                <img src="../../public/imgs/ai_feature3.png">
            </el-carousel-item>
            <el-carousel-item>
                <img src="../../public/imgs/ai_feature4.png">
            </el-carousel-item>
        </el-carousel>
    </div>
  </div>
</template>

<script>
export default {
    name:'FeatuerPage',
    data() {
        return {
            
        }
    },
    methods: {
        go_next(){
            alert('下一张')
        },
        go_prev(){
            alert('上一张')
        }
    },
    mounted() {
        this.$wow.init();
    },
}
</script>

<style scoped>
    #conter{
        width: 100%;
        height: 700px;
        margin-top: 150px;
    }
    #gallery{
        width: 1250px;
        height: 626px;
        position: relative;
        left: 0;
        right: 0;
        margin: 0 auto;
    }
    .el-carousel__item img{
        width: 100%;
        height: 100%;
    }
  
</style>