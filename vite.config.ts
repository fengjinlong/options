import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // // 1. 代理 SEC Ticker 列表
      // '/api/sec-tickers': {
      //   target: 'https://www.sec.gov',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api\/sec-tickers/, '/files/company_tickers.json'),
      //   headers: { 'User-Agent': 'feng58555@gmail.com' }
      // },
      // // 2. 代理 SEC XBRL 财报数据
      // '/api/sec-facts': {
      //   target: 'https://data.sec.gov',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api\/sec-facts/, '/api/xbrl/companyfacts/'),
      //   headers: { 'User-Agent': 'feng58555@gmail.com' }
      // },
      // // 3. 代理 Stooq 历史股价 (CSV)
      // '/api/stooq': {
      //   target: 'https://stooq.com',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api\/stooq/, '/q/d/l/')
      // }
    }
  }
})