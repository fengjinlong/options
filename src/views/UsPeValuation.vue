<template>
  <div class="pe-analyzer">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>美股 PE 估值分析 (Python 强力驱动)</span>
        </div>
      </template>

      <el-form :inline="true">
        <el-form-item label="股票代码">
          <el-select v-model="symbol" filterable allow-create default-first-option clearable placeholder="请输入或选择股票代码"
            style="width: 200px">
            <el-option v-for="item in symbolOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="历史年限">
          <el-input-number v-model="years" :min="1" :max="10" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="fetchData">开始分析</el-button>
        </el-form-item>
      </el-form>

      <div v-if="apiData" class="summary-cards">
        <el-statistic title="当前 PE" :value="apiData.current_pe" :precision="2" />
        <el-statistic title="历史分位" :value="apiData.percentile" :precision="2">
          <template #suffix>%</template>
        </el-statistic>
      </div>

      <div ref="chartRef" class="chart-container" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script setup lang="js">
import { ref, onMounted, onUnmounted, shallowRef } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const symbol = ref('NVDA')
const symbolOptions = ['TSLA', 'KO', 'AAPL', 'NVDA']
const years = ref(3)
const loading = ref(false)
const apiData = ref(null)

const chartRef = ref(null)
const chartInstance = shallowRef(null)

const fetchData = async () => {
  if (!symbol.value) return ElMessage.warning('请输入代码')

  loading.value = true
  try {
    // 直接呼叫 Python 启动的本地 API
    const response = await axios.get(`/api/analyze`, {
      params: { symbol: symbol.value, years: years.value }
    })

    apiData.value = response.data
    renderChart(apiData.value)
    ElMessage.success('Python 数据解析成功！')

  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '数据获取失败')
  } finally {
    loading.value = false
  }
}

const renderChart = (data) => {
  if (!chartInstance.value) chartInstance.value = echarts.init(chartRef.value)

  const dates = data.chart_data.map(item => item.Date)
  const peValues = data.chart_data.map(item => item.PE)

  const option = {
    title: { text: `${data.symbol} P/E Ratio (${data.years} Years)`, left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: '5%', right: '15%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value', scale: true },
    series: [
      {
        name: 'Daily PE',
        type: 'line',
        data: peValues,
        itemStyle: { color: '#1f77b4' },
        showSymbol: false,
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: data.p20, name: '20% 分位', itemStyle: { color: 'green' }, label: { formatter: `20% (${data.p20})` } },
            { yAxis: data.p80, name: '80% 分位', itemStyle: { color: 'orange' }, label: { formatter: `80% (${data.p80})` } },
            { yAxis: data.current_pe, name: 'Current', itemStyle: { color: 'red' }, lineStyle: { type: 'solid', width: 2 }, label: { formatter: `Current (${data.current_pe})` } }
          ]
        },
        markArea: {
          itemStyle: { color: 'rgba(128, 128, 128, 0.15)' },
          data: [[{ yAxis: data.p20 }, { yAxis: data.p80 }]]
        }
      }
    ]
  }
  chartInstance.value.setOption(option)
}

onMounted(() => {
  window.addEventListener('resize', () => chartInstance.value?.resize())
})
onUnmounted(() => {
  window.removeEventListener('resize', () => chartInstance.value?.resize())
  chartInstance.value?.dispose()
})
</script>

<style scoped>
.pe-analyzer {
  max-width: 1000px;
  margin: 20px auto;
}

.summary-cards {
  display: flex;
  gap: 40px;
  justify-content: center;
  margin: 20px 0;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.chart-container {
  width: 100%;
  height: 500px;
}
</style>