<template>
  <div id="conter">
    <div id="outdoor">
        <p class="wenzi">
            process on 1 <br>
            <span style="font-size:16px;position:relative;top:-72px">分辨食物</span>
        </p>
        <button
            @click="goOutndoor" 
            class="view wow animate__animated animate__jackInTheBox animate__slow btns"
            id="outdoorView"
            style="cursor:pointer"
        >
            view-it
        </button>
    </div>
    <div id="indoor">
        <p class="wenzi">
            process on 2 <br>
            <span style="font-size:16px;position:relative;top:-72px">输出rag</span>
        </p>
        <button 
            @click="goIndoor" 
            class="view wow animate__animated animate__jackInTheBox animate__slow btns"
            id="indoorView"
            style="cursor:pointer"
        >
            view-it
        </button>
    </div>
  </div>
</template>

<script>
export default {
    name:'WhichDoor',
    data() {
        return {
            
        }
    },
    methods: {
        goOutndoor(){
            let outdoorView = document.querySelector('#outdoorView')
            outdoorView.className = 'view disable animate__animated animate__zoomOutRight'
            outdoorView.style.backgroundColor='#FFFFFF'
            outdoorView.style.color="black";
            setTimeout(() => {
                outdoorView.style.visibility="hidden"
                this.$router.push('/outdoor')
            }, 1000);
        },
        goIndoor(){
            let indoorView = document.querySelector('#indoorView')
            indoorView.className = 'view disable animate__animated animate__zoomOutRight'
            indoorView.style.backgroundColor='#FFFFFF'
            indoorView.style.color="black";
            setTimeout(() => {
                indoorView.style.visibility="hidden"
                this.$router.push('/indoor')
            }, 1000);
        }
    },
    mounted() {
        this.$wow.init()
    },
}
</script>

<style scoped>
    #conter{
        width: 100%;
        margin-top: 100px;
        background-color: #E9E9E9;
    }
    #outdoor{
        width: 100%;
        height: 100vh;
        background: url('../../public/imgs/food1.png') no-repeat;
        background-size: 100% 100%;
        background-attachment: fixed;
    }
    #indoor{
        width: 100%;
        height: 100vh;
        background: url('../../public/imgs/food2.png') no-repeat;
        background-size: 100% 100%;
        background-attachment: fixed;
    }
    .wenzi{
        font-size: 5rem;
        color:#FFFFFF;
        margin-left: 95px;
        position: relative;
        top: 240px;
    }
    .view.disable{
        --animate-duration: 1s;
    }
    .view{
        display: block;
        width: 200px;
        height: 200px;
        line-height: 200px;
        font-size: 2rem;
        color: #FFFFFF;
        text-align: center;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.2);
        border: #FFFFFF 1px solid;
        position: relative;
        left: 246px;
        top: 208.9px;
        transition:all .6s;
    }
    .view:hover{
        background-color: #FFFFFF;
        color: black;
    }
    /*设置按钮样式*/
    .btns{
        position: relative;
        margin-top: 2%;
    }
</style>