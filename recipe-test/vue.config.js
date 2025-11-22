const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  devServer: {
    host: '0.0.0.0', // 监听所有网卡，允许局域网访问
    port: 8080,      // 前端端口
    allowedHosts: "all", // 关键：允许所有主机访问，替代旧版disableHostCheck
    hot: true, // 关键：强制开启热更新
    liveReload: true // 辅助自动刷新，兜底用
  }
}