<script setup lang="ts">
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
          >历史波动率</el-button
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
}
</style>
