<template>
  <div class="pe-analyzer">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>A股 PE 估值分析 (BaoStock 强力驱动)</span>
        </div>
      </template>

      <el-form :inline="true">
        <el-form-item label="股票代码">
          <el-select v-model="symbol" filterable allow-create placeholder="请输入或选择股票代码 (如 sh.600519)"
            style="width: 220px">
            <el-option v-for="item in symbolOptions" :key="item.value" :label="item.label" :value="item.value" />
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
        <el-statistic title="股票名称" :value="apiData.stock_name" />
        <el-statistic title="当前股价" :value="apiData.current_price" :precision="2" />
        <el-statistic title="当前 PE(TTM)" :value="apiData.current_pe" :precision="2" />
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

// 默认查询茅台
const symbol = ref('sh.600519')
// A股预设选项 (带上前缀方便点击)
const symbolOptions = [
  { label: '贵州茅台 (sh.600519)', value: 'sh.600519' },
  { label: '平安银行 (sz.000001)', value: 'sz.000001' },
  { label: '宁德时代 (sz.300750)', value: 'sz.300750' },
  { label: '紫金矿业 (sh.601899)', value: 'sh.601899' }
]

const years = ref(3)
const loading = ref(false)
const apiData = ref(null)

const chartRef = ref(null)
const chartInstance = shallowRef(null)

const fetchData = async () => {
  if (!symbol.value) return ElMessage.warning('请输入股票代码')

  // 简单校验格式
  const symbolVal = symbol.value.trim()
  if (!/^(sh|sz)\.\d{6}$/.test(symbolVal)) {
    ElMessage.warning('股票代码格式错误，请使用如 sh.600519 或 sz.000001 格式')
    return
  }

  loading.value = true
  try {
    // 调用 A股 专属路由 (请确保 IP 和端口与你的 FastAPI 一致)
    const response = await axios.get(`http://117.72.63.11:8000/api/analyze_cn`, {
      params: { symbol: symbol.value, years: years.value }
    })

    apiData.value = response.data
    renderChart(apiData.value)
    ElMessage.success('A股数据解析成功！')

  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '数据获取失败，请检查代码格式')
  } finally {
    loading.value = false
  }
}

const renderChart = (data) => {
  if (!chartInstance.value) chartInstance.value = echarts.init(chartRef.value)

  const dates = data.chart_data.map(item => item.Date)
  const peValues = data.chart_data.map(item => item.PE)

  const option = {
    // 动态生成包含中文名的标题
    title: {
      text: `${data.stock_name} (${data.symbol}) 历史 PE 走势 - 回溯 ${data.years} 年`,
      left: 'center',
      top: 10
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        const date = params[0].name;
        const pe = params[0].value;
        return `${date}<br/>PE(TTM): <b>${pe.toFixed(2)}</b>`;
      }
    },
    grid: { left: '5%', right: '15%', bottom: '10%', top: '20%', containLabel: true },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value', scale: true, name: 'P/E Ratio' },
    series: [
      {
        name: 'Daily PE',
        type: 'line',
        data: peValues,
        itemStyle: { color: '#1f77b4' },
        showSymbol: false,
        // 新增：自动标注最高点和最低点的气泡
        // 优化后的极值标注（仅文字，无气泡图标）
        markPoint: {
          symbol: 'none',
          label: {
            show: true,
            fontWeight: 'bold',
            formatter: function (param) {
              return `${param.name}: ${param.value.toFixed(2)}`;
            }
          },
          data: [
            { type: 'max', name: '最高', label: { position: 'top', color: '#d62728' } },
            { type: 'min', name: '最低', label: { position: 'bottom', color: '#2ca02c' } }
          ]
        },
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: data.p20, name: '20% 分位', itemStyle: { color: 'green' }, label: { formatter: `20% (${data.p20})`, position: 'end' } },
            { yAxis: data.p80, name: '80% 分位', itemStyle: { color: 'orange' }, label: { formatter: `80% (${data.p80})`, position: 'end' } },
            { yAxis: data.current_pe, name: '当前 PE', itemStyle: { color: 'red' }, lineStyle: { type: 'solid', width: 2 }, label: { formatter: `当前 (${data.current_pe})`, position: 'end' } }
          ]
        },
        // 核心估值区间灰色填充
        markArea: {
          itemStyle: { color: 'rgba(128, 128, 128, 0.15)' },
          data: [[{ yAxis: data.p20 }, { yAxis: data.p80 }]]
        }
      }
    ]
  }

  // 渲染前清除旧数据，防止切换股票时标线残留
  chartInstance.value.clear();
  chartInstance.value.setOption(option)
}

onMounted(() => {
  window.addEventListener('resize', () => chartInstance.value?.resize())
  // 页面加载后自动触发一次茅台的数据请求 (可选)
  // fetchData() 
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
  border: 1px solid #ebeef5;
}

/* 覆盖 Element Plus 统计组件的样式，让文字更大更显眼 */
:deep(.el-statistic__title) {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.chart-container {
  width: 100%;
  height: 550px;
}
</style>