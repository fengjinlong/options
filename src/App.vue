<script setup lang="ts">
import OptionsCalculator from "./components/OptionsCalculator.vue";
import "element-plus/dist/index.css";
</script>

<template>
  <div class="app">
    <OptionsCalculator />
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
  padding: 20px;
}
</style>
