import VueRouter from "vue-router";
import Home from "../pages/Home.vue";
import YeMian from "../pages/zhuye/YeMian.vue";
import AboutUs from "../pages/zhuye/AboutUs.vue";
import chatPag from "../pages/chat/chatPage.vue";

const router = new VueRouter({
  routes: [
    {
      path: "/",
      meta: { isAuth: true },
      component: Home,
      redirect: "/yemian",
      children: [
        // {
        //     //这是param参数的接受要求，首先要申明name然后在path上用：进行占位操作
        //     path:'mycount',
        //     name:'Login',
        //     meta:{isAuth:true,requiresAuth: true},
        //     component: MyCount,
        //     //可在params参数的传递中直接配置props进行参数的简化，后继可以直接props接受使用
        //     props:true,
        //     children:[
        //         {
        //             path:'myhistory',
        //             meta:{isAuthenticated:true},
        //             component: MyHistory,
        //             children:[
        //                 {
        //                     path:'allding',
        //                     component:AllDing
        //                 },
        //                 {
        //                     path:'cancel',
        //                     component:CancelDing
        //                 },
        //                 {
        //                     path:'successding',
        //                     component:SuccessDing
        //                 }
        //             ]
        //         },
        //         {
        //             path: 'myinform',
        //             meta:{isAuth:true,isAuthenticated:true},
        //             component: MyInfrom
        //         },
        //         {
        //             path:'myfix',
        //             meta:{isAuthenticated:true},
        //             component:MyFix
        //         },
        //         {
        //             path:'mymoney',
        //             component:MyMoney
        //         },
        //         {
        //             path:'addroom',
        //             component:AddRoom
        //         }
        //     ]
        // },
        {
          path: "aboutUs",
          meta: { isAuth: true },
          component: AboutUs,
        },
        {
          path: "yemian",
          component: YeMian,
          meta: { isAuth: true },
        },
        {
            path:"chatpage",
            meta: { isAuth: true },
            component: chatPag
        }
      ],
    },
  ],
});


//前置路由守卫
router.beforeEach((to, from, next) => {
    // 让页面回到顶部
    if(to.meta.isAuthenticated){
        const isOnline = localStorage.getItem("isOnline")
        if(isOnline){
            document.documentElement.scrollTop = 0;
            next()
        }else{
            if(confirm('该功能需要登陆，你要登陆吗？')) router.push({path:'/register'})
        }
    }else{
        if(to.meta.isAuth){
            document.documentElement.scrollTop = 0;
        }
        next()
    }
});


export default router;
