<script setup lang="ts">
import { el } from "element-plus/es/locales.mjs";
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="nav-buttons">
        <el-button @click="router.push('/')" type="primary">策略组合</el-button>
        <el-button @click="router.push('/calendar-call')" type="success"
          >日历差价看涨</el-button
        >
        <el-button @click="router.push('/sol-volatility')" type="warning"
          >历史波动率(coingecko)</el-button
        >
        <el-button type="primary" @click="router.push('/cmc-volatility')"
          >历史波动率(coindesk)</el-button
        >
        <el-button type="primary" @click="router.push('/derbit-volatility')"
          >历史波动率(derbit)</el-button
        >
        <el-button type="primary" @click="router.push('/dvol-chart')"
          >DVOL</el-button
        >
        <el-button type="primary" @click="router.push('/options-calculator')"
          >期权价格估算</el-button
        >
        <el-button type="primary" @click="router.push('/sjfx')"
          >加密项目估值分析</el-button
        >
        <el-button type="success" @click="router.push('/sjfx2')"
          >加密项目估值分析2</el-button
        >
        <!-- 看涨期权评估 -->
        <el-button type="success" @click="router.push('/long-call-price')"
          >看涨期权价格评估</el-button
        >
      </div>
    </header>
    <router-view></router-view>
  </div>
</template>

<style>
.app {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
}

.header {
  background-color: #f8f9fa;
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
  margin-bottom: 15px;
}

.nav-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .nav-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-buttons .el-button {
    margin-bottom: 5px;
  }
}
</style>
