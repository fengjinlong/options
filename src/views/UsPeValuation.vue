<template>
  <div class="pe-analyzer">
    <el-card class="box-card" style="margin-bottom: 12px">
      <template #header>
        <div class="card-header">
          <span>美股 PE 估值分析 (新逻辑量化版) — {{ symbol }}</span>
        </div>
      </template>
      <el-form :inline="true">
        <el-form-item label="股票代码">
          <el-select v-model="symbol" filterable allow-create placeholder="输入股票代码" style="width: 200px">
            <el-option v-for="item in symbolOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="panels-row">
      <div class="panel-wrap">
        <el-card class="box-card" v-loading="panel1.loading">
          <template #header>
            <div class="card-header">近 1 年</div>
          </template>

          <div v-if="panel1.data.length > 0" class="summary-cards">
            <el-statistic title="当前 PE（TTM）" :value="panel1CurrentPe" :precision="2" />
            <el-statistic title="历史分位（高=贵）" :value="panel1Percentile" :precision="2">
              <template #suffix>%</template>
            </el-statistic>
            <el-statistic title="有效交易日" :value="panel1.data.length" />
          </div>

          <div v-if="panel1.data.length > 0" class="percentile-info">
            <el-tag v-for="p in panel1PercentileLevels" :key="p.label" :type="p.type" style="margin-right: 12px">
              {{ p.label }}: {{ p.value.toFixed(2) }}
            </el-tag>
            <el-tag type="danger" style="margin-left: 8px">当前: {{ panel1CurrentPe.toFixed(2) }}</el-tag>
          </div>

          <div ref="chartRef1" class="chart-container"></div>
        </el-card>
      </div>

      <div class="panel-wrap">
        <el-card class="box-card" v-loading="panel2.loading">
          <template #header>
            <div class="card-header">近 2 年</div>
          </template>

          <div v-if="panel2.data.length > 0" class="summary-cards">
            <el-statistic title="当前 PE（TTM）" :value="panel2CurrentPe" :precision="2" />
            <el-statistic title="历史分位（高=贵）" :value="panel2Percentile" :precision="2">
              <template #suffix>%</template>
            </el-statistic>
            <el-statistic title="有效交易日" :value="panel2.data.length" />
          </div>

          <div v-if="panel2.data.length > 0" class="percentile-info">
            <el-tag v-for="p in panel2PercentileLevels" :key="p.label" :type="p.type" style="margin-right: 12px">
              {{ p.label }}: {{ p.value.toFixed(2) }}
            </el-tag>
            <el-tag type="danger" style="margin-left: 8px">当前: {{ panel2CurrentPe.toFixed(2) }}</el-tag>
          </div>

          <div ref="chartRef2" class="chart-container"></div>
        </el-card>
      </div>

      <div class="panel-wrap">
        <el-card class="box-card" v-loading="panel3.loading">
          <template #header>
            <div class="card-header">近 3 年</div>
          </template>

          <div v-if="panel3.data.length > 0" class="summary-cards">
            <el-statistic title="当前 PE（TTM）" :value="panel3CurrentPe" :precision="2" />
            <el-statistic title="历史分位（高=贵）" :value="panel3Percentile" :precision="2">
              <template #suffix>%</template>
            </el-statistic>
            <el-statistic title="有效交易日" :value="panel3.data.length" />
          </div>

          <div v-if="panel3.data.length > 0" class="percentile-info">
            <el-tag v-for="p in panel3PercentileLevels" :key="p.label" :type="p.type" style="margin-right: 12px">
              {{ p.label }}: {{ p.value.toFixed(2) }}
            </el-tag>
            <el-tag type="danger" style="margin-left: 8px">当前: {{ panel3CurrentPe.toFixed(2) }}</el-tag>
          </div>

          <div ref="chartRef3" class="chart-container"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="js">
import { ref, reactive, computed, nextTick, onMounted, onUnmounted, watch, markRaw } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import epsJson from './eps.json'

// ==================== 状态配置 ====================
const symbol = ref('NVDA')
const symbolOptions = ['NVDA', 'TSLA', 'AAPL', 'GOOGL', 'KO', 'MSFT', 'AMZN', 'META']
const FMP_API_KEY = 'wQdt9jraXnrDCjOJVwELhblzjyBEXbI3'

// ==================== 纯净 EPS 数据流响应（仅接收核心业务字段） ====================
const epsData = computed(() => {
  const entries = epsJson[symbol.value]
  if (entries && entries.length > 0) {
    return entries.map(e => ({
      year: Number(e.year),
      quarter: e.quarter,
      eps: Number(e.eps)
    }))
  }
  return []
})

// 三面板响应式状态
function createPanel() {
  return reactive({ data: [], loading: false, chartInstance: null })
}
const panel1 = createPanel(); const panel2 = createPanel(); const panel3 = createPanel()
const chartRef1 = ref(null); const chartRef2 = ref(null); const chartRef3 = ref(null)

// ==================== 统一统计指标计算（1/2/3年抽象函数） ====================
function getPanelMetrics(panel) {
  const currentPe = computed(() => panel.data.length > 0 ? panel.data[panel.data.length - 1].pe : 0)
  const percentile = computed(() => {
    if (panel.data.length === 0) return 0
    const all = panel.data.map(d => d.pe)
    const cur = all[all.length - 1]
    return (all.filter(p => p <= cur).length / all.length) * 100
  })
  const percentileLevels = computed(() => {
    if (panel.data.length === 0) return []
    const sorted = [...panel.data.map(d => d.pe)].sort((a, b) => a - b)
    const n = sorted.length
    return [
      { label: '5% 分位', value: sorted[Math.floor(n * 0.05)], type: 'info' },
      { label: '25% 分位', value: sorted[Math.floor(n * 0.25)], type: 'success' },
      { label: '50% 分位', value: sorted[Math.floor(n * 0.50)], type: 'warning' },
      { label: '75% 分位', value: sorted[Math.floor(n * 0.75)], type: 'warning' },
      { label: '95% 分位', value: sorted[Math.floor(n * 0.95)], type: 'info' },
    ]
  })
  return { currentPe, percentile, percentileLevels }
}

const { currentPe: panel1CurrentPe, percentile: panel1Percentile, percentileLevels: panel1PercentileLevels } = getPanelMetrics(panel1)
const { currentPe: panel2CurrentPe, percentile: panel2Percentile, percentileLevels: panel2PercentileLevels } = getPanelMetrics(panel2)
const { currentPe: panel3CurrentPe, percentile: panel3Percentile, percentileLevels: panel3PercentileLevels } = getPanelMetrics(panel3)

// ==================== 核心量化对齐算法 ====================
function calculateTtmEpsForDate(priceDate, epsEntriesWithDate) {
  const available = epsEntriesWithDate.filter(e => e._reportDate <= priceDate)
  if (available.length < 4) return { ttmEps: 0, usedQuarters: [], hasEnoughData: false }
  const recent4 = available.slice(-4)
  return {
    ttmEps: recent4.reduce((sum, e) => sum + e.eps, 0),
    usedQuarters: recent4.map(e => `${e.year} ${e.quarter}`),
    hasEnoughData: true,
  }
}

function buildDailyPeSeries(priceResult, epsEntries, historyYears) {
  const dailyPrices = priceResult.daily_prices
  const sortedDates = Object.keys(dailyPrices).sort()
  if (sortedDates.length === 0) return []

  const cutoffDate = new Date()
  cutoffDate.setFullYear(cutoffDate.getFullYear() - historyYears)
  const cutoffStr = cutoffDate.toISOString().split('T')[0]
  const filteredDates = sortedDates.filter(d => d >= cutoffStr)

  const results = []
  for (const dateStr of filteredDates) {
    const price = dailyPrices[dateStr]
    const { ttmEps, usedQuarters, hasEnoughData } = calculateTtmEpsForDate(dateStr, epsEntries)
    if (!hasEnoughData || ttmEps <= 0) continue

    results.push({
      date: dateStr,
      price,
      pe: Number((price / ttmEps).toFixed(4)),
      ttmEps: Number(ttmEps.toFixed(4)),
      usedQuarters,
    })
  }
  return results
}

// FMP 历史价格网络请求
async function getPriceFmp(symbolStr, apiKey, historyYears) {
  const baseUrl = 'https://financialmodelingprep.com/stable'
  const today = new Date()
  const fromDate = new Date(today)
  fromDate.setFullYear(fromDate.getFullYear() - historyYears)
  const fromStr = fromDate.toISOString().split('T')[0]
  const toStr = today.toISOString().split('T')[0]

  const response = await axios.get(`${baseUrl}/historical-price-eod/full`, {
    params: { symbol: symbolStr, from: fromStr, to: toStr, apikey: apiKey },
    timeout: 30000,
  })

  const priceData = response.data
  const histList = Array.isArray(priceData) ? priceData : (priceData.historical || [])
  const dailyCloseDict = {}

  for (const dayData of histList) {
    const dateStr = dayData.date
    const closePrice = dayData.close
    if (dateStr && closePrice !== undefined && closePrice !== null && dateStr >= fromStr) {
      dailyCloseDict[dateStr] = Number(Number(closePrice).toFixed(2))
    }
  }
  return { symbol: symbolStr, daily_prices: dailyCloseDict }
}

// ==================== 异步流水线（新逻辑核心） ====================
async function fetchPanel(panel, years) {
  const validEps = epsData.value.filter(r => r.year && r.quarter && r.eps !== null && r.eps !== undefined)
  if (validEps.length < 4) return

  panel.loading = true
  panel.data = []

  try {
    const priceResult = await getPriceFmp(symbol.value, FMP_API_KEY, years)
    const dailyPrices = priceResult.daily_prices
    const sortedDates = Object.keys(dailyPrices).sort()
    if (sortedDates.length === 0) return

    const latestPriceDate = sortedDates[sortedDates.length - 1]

    // 严格按时间序正向排列财报
    const sortedEps = [...validEps].sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year
      return ['Q1', 'Q2', 'Q3', 'Q4'].indexOf(a.quarter) - ['Q1', 'Q2', 'Q3', 'Q4'].indexOf(b.quarter)
    })

    // 【核心新逻辑：智能时间轴推导与钳制】
    const epsEntries = sortedEps.map((e, idx) => {
      // 采用美股标准宽限期末端锚点，斩断前瞻偏差
      const standardMapping = { Q1: '04-30', Q2: '07-31', Q3: '10-31', Q4: '02-15' }
      const reportYear = e.quarter === 'Q4' ? e.year + 1 : e.year
      let inferredDate = `${reportYear}-${standardMapping[e.quarter]}`

      // 【黄金钳制法则】：若最新追加入的数据推导出的披露日在未来，强制对齐当前最新交易日，使模型在当下立即穿透生效
      if (idx === sortedEps.length - 1 && inferredDate > latestPriceDate) {
        inferredDate = latestPriceDate
      }
      return { ...e, _reportDate: inferredDate }
    })

    const dailyPeData = buildDailyPeSeries(priceResult, epsEntries, years)
    if (dailyPeData.length === 0) return

    panel.data = dailyPeData
  } catch (error) {
    console.error(`[${years}年面板] 核心流水线异常:`, error)
  } finally {
    panel.loading = false
  }
}

function clearAllCharts() {
  ;[panel1, panel2, panel3].forEach(p => {
    p.data = []
    p.chartInstance?.dispose()
    p.chartInstance = null
  })
}

async function autoFetchAll() {
  await Promise.all([fetchPanel(panel1, 1), fetchPanel(panel2, 2), fetchPanel(panel3, 3)])
}

// 监听数据资产变动，触发 HMR 级别热响应
watch(epsData, (newVal) => {
  if (!newVal || newVal.length < 4) {
    ElMessage.warning(`未检测到股票 ${symbol.value} 的有效本地数据`)
    return
  }
  clearAllCharts()
  autoFetchAll()
}, { immediate: true })

// ==================== Echarts 渲染引擎 ====================
function safeRenderChart(panel, chartRefEl, years) {
  if (!chartRefEl || !panel.data.length) return
  if (!panel.chartInstance) panel.chartInstance = markRaw(echarts.init(chartRefEl))

  const data = panel.data
  const dates = data.map(d => d.date)
  const peValues = data.map(d => d.pe)
  const sorted = [...peValues].sort((a, b) => a - b)
  const n = sorted.length

  const p10 = sorted[Math.floor(n * 0.10)]
  const p50 = sorted[Math.floor(n * 0.50)]
  const p90 = sorted[Math.floor(n * 0.90)]
  const cur = peValues[peValues.length - 1]

  const option = {
    backgroundColor: '#ffffff',
    title: { text: `${symbol.value} P/E Ratio (TTM) — 近 ${years} 年`, left: 'center', top: 5, textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderWidth: 1,
      borderColor: '#ddd',
      textStyle: { fontSize: 12, color: '#333' },
      formatter(params) {
        const d = params[0]
        if (!d || d.dataIndex === undefined) return ''
        const raw = data[d.dataIndex]
        return `
          <div>
            <strong>交易日: ${d.axisValue}</strong><br/>
            PE(TTM): <strong style="color:#5470c6">${d.value.toFixed(2)}</strong><br/>
            收盘价: $${raw.price.toFixed(2)} | TTM EPS: $${raw.ttmEps.toFixed(4)}<br/>
            <span style="color:#888; font-size:11px">分母构成: ${raw.usedQuarters.join(' + ')}</span>
          </div>`
      }
    },
    legend: { data: ['PE(TTM)', '10%分位', '50%分位', '90%分位', '当前'], top: 38 },
    grid: { left: '5%', right: '5%', top: 80, bottom: '15%' },
    xAxis: { type: 'category', data: dates, boundaryGap: false, axisLabel: { rotate: 30, fontSize: 9 } },
    yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    dataZoom: [{ type: 'inside', xAxisIndex: 0 }, { type: 'slider', xAxisIndex: 0, bottom: 15, height: 18 }],
    series: [{
      name: 'PE(TTM)',
      type: 'line',
      data: peValues,
      showSymbol: false,
      lineStyle: { width: 1.5, color: '#5470c6' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(100,149,237,0.2)' },
          { offset: 1, color: 'rgba(100,149,237,0.01)' }
        ])
      },
      markLine: {
        silent: true, symbol: 'none',
        label: { fontSize: 10, position: 'insideEndTop' },
        data: [
          { yAxis: p10, lineStyle: { color: '#52c41a', type: 'dashed' }, label: { formatter: `10% (${p10.toFixed(1)})`, color: '#52c41a' } },
          { yAxis: p50, lineStyle: { color: '#faad14', type: 'dashed' }, label: { formatter: `50% (${p50.toFixed(1)})`, color: '#faad14' } },
          { yAxis: p90, lineStyle: { color: '#f5222d', type: 'dashed' }, label: { formatter: `90% (${p90.toFixed(1)})`, color: '#f5222d' } },
          { yAxis: cur, lineStyle: { color: '#722ed1', width: 2 }, label: { formatter: `当前 (${cur.toFixed(1)})`, color: '#722ed1' } }
        ]
      }
    }]
  }
  panel.chartInstance.setOption(option, true)
}

// 绑定各面板渲染动力源
watch([chartRef1, () => panel1.data], ([el, d]) => { if (el && d.length) nextTick(() => safeRenderChart(panel1, el, 1)) })
watch([chartRef2, () => panel2.data], ([el, d]) => { if (el && d.length) nextTick(() => safeRenderChart(panel2, el, 2)) })
watch([chartRef3, () => panel3.data], ([el, d]) => { if (el && d.length) nextTick(() => safeRenderChart(panel3, el, 3)) })

// ==================== 生命周期 ====================
onMounted(() => { window.addEventListener('resize', handleResize) })
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
    ;[panel1, panel2, panel3].forEach(p => p.chartInstance?.dispose())
})
function handleResize() { [panel1, panel2, panel3].forEach(p => p.chartInstance?.resize()) }
</script>

<style scoped>
.pe-analyzer {
  max-width: 1600px;
  margin: 2px auto;
  padding: 0 4px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.panels-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-cards {
  display: flex;
  gap: 24px;
  justify-content: center;
  flex-wrap: wrap;
  margin: 12px 0;
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.percentile-info {
  text-align: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin: 8px 0;
}
</style>