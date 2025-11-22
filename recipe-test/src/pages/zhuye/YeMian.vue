<template>
  <div>
    <TopPage/>
    <HistoryPage/>
    <FeatuerPage/>
    <WhichDoor/>
    <MyFoods/>
    <ContactUs/>
  </div>
</template>

<script>
import TopPage from '../../components/TopPage.vue';
import HistoryPage from '../../components/HistoryPage.vue';
import FeatuerPage from '../../components/FeatuerPage.vue';
import WhichDoor from '../../components/WhichDoor.vue';
import ContactUs from '../../components/ContactUs.vue';
import MyFoods from '../zhuye/MyFoods.vue'
export default {
    name:'YeMian',
    data() {
        return {
            
        }
    },
    components:{
        TopPage,
        HistoryPage,
        FeatuerPage,
        WhichDoor,
        ContactUs,
        MyFoods
    }
}
</script>

<style>

</style>