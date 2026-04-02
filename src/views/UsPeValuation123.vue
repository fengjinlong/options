<template>
  <div class="pe-analyzer">
    <!-- 顶部：股票选择器 -->
    <el-card class="box-card" style="margin-bottom: 12px">
      <template #header>
        <div class="card-header">
          <span>美股 PE 估值分析 — {{ symbol }}</span>
        </div>
      </template>
      <el-form :inline="true">
        <el-form-item label="股票代码">
          <el-select v-model="symbol" filterable allow-create placeholder="输入股票代码" style="width: 200px"
            @change="onSymbolChange">
            <el-option v-for="item in symbolOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 三面板：1年 | 2年 | 3年 -->
    <div class="panels-row">
      <!-- ===== 1 年面板 ===== -->
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

      <!-- ===== 2 年面板 ===== -->
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

      <!-- ===== 3 年面板 ===== -->
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
import { ref, reactive, computed, nextTick, onMounted, onUnmounted, shallowRef, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import epsJson from './eps.json'

// ==================== 共享状态 ====================
const symbol = ref('NVDA')
const symbolOptions = ['NVDA', 'TSLA', 'AAPL', 'GOOGL', 'MSTR', 'KO', 'MSFT', 'AMZN']
const epsData = ref([])

// FMP API Key
const FMP_API_KEY = 'wQdt9jraXnrDCjOJVwELhblzjyBEXbI3'

// ==================== 双面板独立状态 ====================
function createPanel() {
  return reactive({
    data: [],
    loading: false,
    chartInstance: null,
  })
}

const panel1 = createPanel()
const panel2 = createPanel()
const panel3 = createPanel()
const chartRef1 = ref(null)
const chartRef2 = ref(null)
const chartRef3 = ref(null)

// ==================== 每面板的 computed（直接引用 panel.data）====================
const panel1CurrentPe = computed(() => panel1.data.length > 0 ? panel1.data[panel1.data.length - 1].pe : 0)
const panel1Percentile = computed(() => {
  if (panel1.data.length === 0) return 0
  const all = panel1.data.map(d => d.pe)
  const cur = all[all.length - 1]
  return (all.filter(p => p <= cur).length / all.length) * 100
})
const panel1PercentileLevels = computed(() => {
  if (panel1.data.length === 0) return []
  const sorted = [...panel1.data.map(d => d.pe)].sort((a, b) => a - b)
  const n = sorted.length
  return [
    { label: '5% 分位', value: sorted[Math.floor(n * 0.05)], type: 'info' },
    { label: '25% 分位', value: sorted[Math.floor(n * 0.25)], type: 'success' },
    { label: '50% 分位', value: sorted[Math.floor(n * 0.50)], type: 'warning' },
    { label: '75% 分位', value: sorted[Math.floor(n * 0.75)], type: 'warning' },
    { label: '95% 分位', value: sorted[Math.floor(n * 0.95)], type: 'info' },
  ]
})

const panel2CurrentPe = computed(() => panel2.data.length > 0 ? panel2.data[panel2.data.length - 1].pe : 0)
const panel2Percentile = computed(() => {
  if (panel2.data.length === 0) return 0
  const all = panel2.data.map(d => d.pe)
  const cur = all[all.length - 1]
  return (all.filter(p => p <= cur).length / all.length) * 100
})
const panel2PercentileLevels = computed(() => {
  if (panel2.data.length === 0) return []
  const sorted = [...panel2.data.map(d => d.pe)].sort((a, b) => a - b)
  const n = sorted.length
  return [
    { label: '5% 分位', value: sorted[Math.floor(n * 0.05)], type: 'info' },
    { label: '25% 分位', value: sorted[Math.floor(n * 0.25)], type: 'success' },
    { label: '50% 分位', value: sorted[Math.floor(n * 0.50)], type: 'warning' },
    { label: '75% 分位', value: sorted[Math.floor(n * 0.75)], type: 'warning' },
    { label: '95% 分位', value: sorted[Math.floor(n * 0.95)], type: 'info' },
  ]
})

const panel3CurrentPe = computed(() => panel3.data.length > 0 ? panel3.data[panel3.data.length - 1].pe : 0)
const panel3Percentile = computed(() => {
  if (panel3.data.length === 0) return 0
  const all = panel3.data.map(d => d.pe)
  const cur = all[all.length - 1]
  return (all.filter(p => p <= cur).length / all.length) * 100
})
const panel3PercentileLevels = computed(() => {
  if (panel3.data.length === 0) return []
  const sorted = [...panel3.data.map(d => d.pe)].sort((a, b) => a - b)
  const n = sorted.length
  return [
    { label: '5% 分位', value: sorted[Math.floor(n * 0.05)], type: 'info' },
    { label: '25% 分位', value: sorted[Math.floor(n * 0.25)], type: 'success' },
    { label: '50% 分位', value: sorted[Math.floor(n * 0.50)], type: 'warning' },
    { label: '75% 分位', value: sorted[Math.floor(n * 0.75)], type: 'warning' },
    { label: '95% 分位', value: sorted[Math.floor(n * 0.95)], type: 'info' },
  ]
})

// ==================== EPS 数据来源（从 eps.json 加载）====================
function loadEpsFromJson(sym) {
  const entries = epsJson[sym]
  if (!entries || entries.length === 0) return null
  return entries.map(e => ({ year: e.year, quarter: e.quarter, eps: e.eps }))
}

function loadFromStorage() {
  const fromJson = loadEpsFromJson(symbol.value)
  if (fromJson) {
    epsData.value = fromJson
    return true
  }
  const raw = localStorage.getItem(`pe_eps_${symbol.value}`)
  if (raw) {
    try {
      epsData.value = JSON.parse(raw)
      return true
    } catch {
      return false
    }
  }
  return false
}

function onSymbolChange() {
  panel1.data = []
  panel1.chartInstance?.dispose()
  panel1.chartInstance = null
  panel2.data = []
  panel2.chartInstance?.dispose()
  panel2.chartInstance = null
  panel3.data = []
  panel3.chartInstance?.dispose()
  panel3.chartInstance = null
  loadFromStorage()
  autoFetchAll()
}

// ==================== 核心算法：计算每日 PE TTM ====================
function deriveReportDate(epsEntry) {
  const quarterToMonth = { Q1: '05-01', Q2: '08-01', Q3: '11-01', Q4: '02-01' }
  const monthDay = quarterToMonth[epsEntry.quarter] || '05-01'
  const reportYear = epsEntry.quarter === 'Q4' ? epsEntry.year + 1 : epsEntry.year
  return `${reportYear}-${monthDay}`
}

function calculateTtmEpsForDate(priceDate, epsEntries) {
  const epsWithDate = epsEntries.map(e => ({ ...e, _reportDate: deriveReportDate(e) }))
  const available = epsWithDate
    .filter(e => e._reportDate <= priceDate)
    .sort((a, b) => a._reportDate.localeCompare(b._reportDate))

  if (available.length < 4) {
    return { ttmEps: 0, usedQuarters: [], hasEnoughData: false }
  }

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

// ==================== 价格数据获取（FMP API）====================
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

// ==================== 单面板数据获取 ====================
async function fetchPanel(panel, years) {
  const validEps = epsData.value.filter(r => r.year && r.quarter && r.eps !== null && r.eps !== undefined && r.eps !== 0)
  if (validEps.length < 4) return

  panel.loading = true
  panel.data = []

  try {
    const epsEntries = validEps
      .map(e => ({ year: Number(e.year), quarter: e.quarter, eps: Number(e.eps) }))
      .sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year
        return ['Q1', 'Q2', 'Q3', 'Q4'].indexOf(a.quarter) - ['Q1', 'Q2', 'Q3', 'Q4'].indexOf(b.quarter)
      })

    const priceResult = await getPriceFmp(symbol.value, FMP_API_KEY, years)
    if (Object.keys(priceResult.daily_prices).length === 0) return

    const dailyPeData = buildDailyPeSeries(priceResult, epsEntries, years)
    if (dailyPeData.length === 0) return

    panel.data = dailyPeData
  } catch (error) {
    console.error(`[${years}年] 数据获取失败:`, error)
  } finally {
    panel.loading = false
  }
}

// ==================== 自动加载 ====================
async function autoFetchAll() {
  await Promise.all([
    fetchPanel(panel1, 1),
    fetchPanel(panel2, 2),
    fetchPanel(panel3, 3),
  ])
}

// ==================== 图表渲染（watcher 触发）====================
function safeRenderChart(panel, chartRefEl, years) {
  if (!chartRefEl || !panel.data.length) return

  if (!panel.chartInstance) {
    panel.chartInstance = echarts.init(chartRefEl)
  }

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
    title: {
      text: `${symbol.value} P/E Ratio (TTM) — 近 ${years} 年`,
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 600 },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderWidth: 1,
      borderColor: '#ddd',
      padding: [8, 12],
      textStyle: { fontSize: 12, color: '#333' },
      formatter(params) {
        const d = params[0]
        if (!d || d.dataIndex === undefined) return ''
        const raw = data[d.dataIndex]
        if (!raw) return ''
        const quarters = raw.usedQuarters.join(' + ')
        return `
          <div>
            <strong>${d.axisValue}</strong><br/>
            PE(TTM): <strong style="color:#5470c6">${d.value.toFixed(2)}</strong><br/>
            收盘价: $${raw.price.toFixed(2)}<br/>
            TTM EPS: $${raw.ttmEps.toFixed(4)}<br/>
            <span style="color:#888">分母: ${quarters}</span>
          </div>
        `
      },
    },
    legend: {
      data: ['PE(TTM)', '10%分位', '50%分位', '90%分位', '当前'],
      top: 38,
    },
    grid: {
      left: '6%',
      right: '8%',
      top: 80,
      bottom: '14%',
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLabel: {
        rotate: 30,
        fontSize: 9,
      },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: { formatter: val => val.toFixed(0) },
      splitLine: { lineStyle: { color: '#f0f0f0' } },
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: 0, filterMode: 'none' },
      {
        type: 'slider',
        xAxisIndex: 0,
        bottom: 20,
        height: 20,
        fillerColor: 'rgba(100,149,237,0.1)',
        borderColor: '#ddd',
        z: 1,
      },
    ],
    series: [
      {
        name: 'PE(TTM)',
        type: 'line',
        data: peValues,
        smooth: false,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#5470c6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(100,149,237,0.25)' },
            { offset: 1, color: 'rgba(100,149,237,0.02)' },
          ]),
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { width: 1 },
          label: { fontSize: 10, position: 'insideEndTop' },
          data: [
            {
              yAxis: p10,
              lineStyle: { color: '#52c41a', type: 'dashed' },
              label: { formatter: `10% (${p10.toFixed(1)})`, color: '#52c41a' },
            },
            {
              yAxis: p50,
              lineStyle: { color: '#faad14', type: 'dashed' },
              label: { formatter: `50% (${p50.toFixed(1)})`, color: '#faad14' },
            },
            {
              yAxis: p90,
              lineStyle: { color: '#f5222d', type: 'dashed' },
              label: { formatter: `90% (${p90.toFixed(1)})`, color: '#f5222d' },
            },
            {
              yAxis: cur,
              lineStyle: { color: '#722ed1', type: 'solid', width: 2 },
              label: { formatter: `当前 (${cur.toFixed(1)})`, color: '#722ed1' },
            },
          ],
        },
        markArea: {
          silent: true,
          data: [
            [{ yAxis: p10, itemStyle: { color: 'rgba(82,196,26,0.06)' } }, { yAxis: p50 }],
            [{ yAxis: p50, itemStyle: { color: 'rgba(250,173,20,0.06)' } }, { yAxis: p90 }],
            [{ yAxis: p90, itemStyle: { color: 'rgba(245,34,45,0.08)' } }, { yAxis: sorted[n - 1] + 5 }],
          ],
        },
      },
    ],
  }

  panel.chartInstance.setOption(option, true)
}

// watch chartRef + panel.data，等两者都就绪再渲染
watch([() => chartRef1.value, () => panel1.data], ([el, data]) => {
  if (el && data.length > 0) nextTick(() => safeRenderChart(panel1, el, 1))
})
watch([() => chartRef2.value, () => panel2.data], ([el, data]) => {
  if (el && data.length > 0) nextTick(() => safeRenderChart(panel2, el, 2))
})
watch([() => chartRef3.value, () => panel3.data], ([el, data]) => {
  if (el && data.length > 0) nextTick(() => safeRenderChart(panel3, el, 3))
})

// ==================== 生命周期 ====================
onMounted(() => {
  loadFromStorage()
  autoFetchAll()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  panel1.chartInstance?.dispose()
  panel2.chartInstance?.dispose()
  panel3.chartInstance?.dispose()
})

function handleResize() {
  panel1.chartInstance?.resize()
  panel2.chartInstance?.resize()
  panel3.chartInstance?.resize()
}
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
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  margin: 14px 0;
  background-color: #f8f9fa;
  padding: 14px 20px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.percentile-info {
  text-align: center;
  margin-bottom: 10px;
  font-size: 13px;
}

.chart-container {
  width: 100%;
  height: 420px;
  margin: 10px 0;
}
</style>
