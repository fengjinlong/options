<template>
  <div class="pe-analyzer">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>美股 PE 估值分析 — {{ symbol }}</span>
        </div>
      </template>

      <!-- ==================== 控制区 ==================== -->
      <el-form :inline="true" class="controls-row">
        <el-form-item label="股票代码">
          <el-select v-model="symbol" filterable allow-create placeholder="输入股票代码" style="width: 200px"
            @change="onSymbolChange">
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

      <!-- ==================== 汇总卡片 ==================== -->
      <div v-if="chartData.length > 0" class="summary-cards">
        <el-statistic title="当前 PE（TTM）" :value="currentPe" :precision="2" />
        <el-statistic title="历史分位（高=贵）" :value="percentile" :precision="2">
          <template #suffix>%</template>
        </el-statistic>
        <el-statistic title="有效交易日" :value="chartData.length" />
      </div>

      <!-- ==================== 分位信息 ==================== -->
      <div v-if="chartData.length > 0" class="percentile-info">
        <el-tag v-for="p in percentileLevels" :key="p.label" :type="p.type" style="margin-right: 12px">
          {{ p.label }}: {{ p.value.toFixed(2) }}
        </el-tag>
        <el-tag type="danger" style="margin-left: 8px">当前: {{ currentPe.toFixed(2) }}</el-tag>
      </div>

      <!-- ==================== 图表区 ==================== -->
      <div v-loading="loading">
        <div ref="chartRef" class="chart-container"></div>
      </div>

    </el-card>
  </div>
</template>

<script setup lang="js">
import { ref, computed, onMounted, onUnmounted, shallowRef } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import epsJson from './eps.json'

// ==================== 响应式状态 ====================
const symbol = ref('NVDA')
const symbolOptions = ['NVDA', 'TSLA', 'AAPL', 'GOOGL', 'MSTR', 'KO', 'MSFT', 'AMZN']
const years = ref(3)
const loading = ref(false)
const chartRef = ref(null)
const chartInstance = shallowRef(null)

// EPS 数据表（12行初始值，可动态添加/删除）
const epsData = ref([])
const chartData = ref([])

// FMP API Key（可在 https://site.financialmodelingprep.com/ 免费注册获取）
const FMP_API_KEY = 'wQdt9jraXnrDCjOJVwELhblzjyBEXbI3'

// ==================== 计算属性 ====================
const currentPe = computed(() => {
  return chartData.value.length > 0 ? chartData.value[chartData.value.length - 1].pe : 0
})

const percentile = computed(() => {
  if (chartData.value.length === 0) return 0
  const allPEs = chartData.value.map(d => d.pe)
  const cur = currentPe.value
  // 公式：当前 PE 在历史中的百分位（低 PE = 低百分位 = 便宜，高 PE = 高百分位 = 贵）
  return (allPEs.filter(p => p <= cur).length / allPEs.length) * 100
})

const percentileLevels = computed(() => {
  if (chartData.value.length === 0) return []
  const sorted = [...chartData.value.map(d => d.pe)].sort((a, b) => a - b)
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

function getStorageKey() {
  return `pe_eps_${symbol.value}`
}

function loadFromStorage() {
  // 优先从 eps.json 加载对应股票的数据
  const fromJson = loadEpsFromJson(symbol.value)
  if (fromJson) {
    epsData.value = fromJson
    ElMessage.info(`已从 eps.json 加载 ${symbol.value} 的 ${fromJson.length} 条 EPS 数据`)
    return true
  }
  // eps.json 中无该股票时尝试 localStorage 回退
  const raw = localStorage.getItem(getStorageKey())
  if (raw) {
    try {
      epsData.value = JSON.parse(raw)
      ElMessage.info(`已从本地缓存加载 ${epsData.value.length} 条 EPS 数据`)
      return true
    } catch {
      return false
    }
  }
  return false
}

function onSymbolChange() {
  chartData.value = []
  chartInstance.value?.clear()
  loadFromStorage()
}

// ==================== 核心算法：计算每日 PE TTM ====================

/**
 * 根据 EPS 数据条目，推算其财报"发布日期"。
 *
 * 规则（美股惯例）：
 *   Q1 财报 → 通常在 5 月发布 → treated as available from 5-01
 *   Q2 财报 → 通常在 8 月发布 → treated as available from 8-01
 *   Q3 财报 → 通常在 11 月发布 → treated as available from 11-01
 *   Q4 财报 → 通常在次年 2 月发布 → treated as available from 02-01（次年）
 *
 * @param {Object} epsEntry - 含 year, quarter, eps 的对象
 * @returns {string} 格式 YYYY-MM-DD
 */
function deriveReportDate(epsEntry) {
  const quarterToMonth = { Q1: '05-01', Q2: '08-01', Q3: '11-01', Q4: '02-01' }
  const monthDay = quarterToMonth[epsEntry.quarter] || '05-01'

  // Q4 的财报在次年 2 月发布
  const reportYear = epsEntry.quarter === 'Q4' ? epsEntry.year + 1 : epsEntry.year
  return `${reportYear}-${monthDay}`
}

/**
 * 根据给定的"当前交易日"（priceDate），动态计算当时可用的 TTM EPS。
 *
 * 滚动窗口逻辑（以推导的财报发布日为准）：
 *
 *   1. 遍历所有 EPS 条目，按推导出的报告日期过滤出 <= priceDate 的条目。
 *   2. 取最新（报告日期最晚）的 4 条记录。
 *   3. 求和即为该日的 TTM EPS。
 *
 *   例：priceDate = 2025-01-15
 *     → Q4 2024（2025-02-01）未发布 → 不计入
 *     → Q3 2024（2024-11-01）已发布 → 计入
 *     → 取最近 4 个已发布季度求和
 *
 * @param {string} priceDate  - 格式 YYYY-MM-DD，当前的交易日
 * @param {Array}  epsEntries - EPS 数据数组，每项含 {year, quarter, eps}
 * @returns {{ ttmEps: number, usedQuarters: string[], hasEnoughData: boolean }}
 */
function calculateTtmEpsForDate(priceDate, epsEntries) {
  // 为每条 EPS 推导报告日期
  const epsWithDate = epsEntries.map(e => ({
    ...e,
    _reportDate: deriveReportDate(e),
  }))

  // 筛选出在价格日期当天及之前已发布的财报
  const available = epsWithDate
    .filter(e => e._reportDate <= priceDate)
    .sort((a, b) => a._reportDate.localeCompare(b._reportDate)) // 按报告日期升序

  if (available.length < 4) {
    return { ttmEps: 0, usedQuarters: [], hasEnoughData: false }
  }

  // 取最近 4 个已发布季度
  const recent4 = available.slice(-4)
  const ttmEps = recent4.reduce((sum, e) => sum + e.eps, 0)
  const usedQuarters = recent4.map(e => `${e.year} ${e.quarter}`)

  return { ttmEps, usedQuarters, hasEnoughData: true }
}

/**
 * 遍历每一天的收盘价，计算当天的 PE（TTM）。
 *
 * @param {Object} priceResult       - getNvdaPriceFmp() 返回的价格数据 { symbol, daily_prices }
 * @param {Array}  epsEntries        - 排序后的 EPS 数组
 * @param {number} historyYears      - 拉取几年的价格数据
 * @returns {Array} 每日 PE 明细 [{ date, price, pe, ttmEps, usedQuarters }]
 */
function buildDailyPeSeries(priceResult, epsEntries, historyYears) {
  const dailyPrices = priceResult.daily_prices

  // 按日期排序所有交易日
  const sortedDates = Object.keys(dailyPrices).sort()

  if (sortedDates.length === 0) {
    ElMessage.warning('价格数据为空，无法计算 PE')
    return []
  }

  // 过滤日期范围
  const cutoffDate = new Date()
  cutoffDate.setFullYear(cutoffDate.getFullYear() - historyYears)
  const cutoffStr = cutoffDate.toISOString().split('T')[0]
  const filteredDates = sortedDates.filter(d => d >= cutoffStr)

  const results = []

  for (const dateStr of filteredDates) {
    const price = dailyPrices[dateStr]

    // 计算该日的 TTM EPS
    const { ttmEps, usedQuarters, hasEnoughData } = calculateTtmEpsForDate(dateStr, epsEntries)

    if (!hasEnoughData || ttmEps <= 0) {
      continue // 数据不足或 EPS 无效，跳过该日
    }

    const pe = price / ttmEps

    results.push({
      date: dateStr,
      price,
      pe: Number(pe.toFixed(4)),
      ttmEps: Number(ttmEps.toFixed(4)),
      usedQuarters,
    })
  }

  return results
}

// ==================== 价格数据获取（FMP API）====================
async function getPriceFmp(symbolStr, apiKey, historyYears) {
  const baseUrl = 'https://financialmodelingprep.com/stable'

  // 计算起始日期
  const today = new Date()
  const fromDate = new Date(today)
  fromDate.setFullYear(fromDate.getFullYear() - historyYears)
  const fromStr = fromDate.toISOString().split('T')[0]
  const toStr = today.toISOString().split('T')[0]

  const url = `${baseUrl}/historical-price-eod/full`

  try {
    const response = await axios.get(url, {
      params: {
        symbol: symbolStr,
        from: fromStr,
        to: toStr,
        apikey: apiKey,
      },
      timeout: 30000,
    })

    const priceData = response.data
    // 兼容处理：FMP 新版数据可能是纯列表，也可能包裹在 { historical: [...] } 中
    const histList = Array.isArray(priceData) ? priceData : (priceData.historical || [])

    const dailyCloseDict = {}

    if (Array.isArray(histList) && histList.length > 0) {
      for (const dayData of histList) {
        const dateStr = dayData.date
        const closePrice = dayData.close

        if (dateStr && closePrice !== undefined && closePrice !== null && dateStr >= fromStr) {
          dailyCloseDict[dateStr] = Number(Number(closePrice).toFixed(2))
        }
      }
      console.log(`[getPriceFmp] ✅ 成功获取 ${symbolStr} 收盘价，共 ${Object.keys(dailyCloseDict).length} 个交易日`)
    } else {
      console.warn('[getPriceFmp] ⚠️  接口返回空数据:', priceData)
    }

    return { symbol: symbolStr, daily_prices: dailyCloseDict }

  } catch (error) {
    console.error('[getPriceFmp] ❌ 请求失败:', error)
    throw error
  }
}

// ==================== 主数据流程 ====================
async function fetchData() {
  // 1. 前置校验
  const validEps = epsData.value.filter(r => r.year && r.quarter && r.eps !== null && r.eps !== undefined && r.eps !== 0)
  if (validEps.length < 4) {
    ElMessage.warning('至少需要 4 条有效的 EPS 数据（年份+季度+EPS值）')
    return
  }

  loading.value = true
  chartData.value = []

  try {
    // 2. 整理 EPS 数据（按年份+季度升序排列）
    const epsEntries = validEps
      .map(e => ({
        year: Number(e.year),
        quarter: e.quarter,
        eps: Number(e.eps),
      }))
      .sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year
        return ['Q1', 'Q2', 'Q3', 'Q4'].indexOf(a.quarter) - ['Q1', 'Q2', 'Q3', 'Q4'].indexOf(b.quarter)
      })

    // 3. 获取价格数据
    const priceResult = await getPriceFmp(symbol.value, FMP_API_KEY, years.value)

    if (Object.keys(priceResult.daily_prices).length === 0) {
      ElMessage.error('价格数据为空，请检查股票代码或 API Key')
      return
    }

    // 4. 计算每日 PE TTM
    const dailyPeData = buildDailyPeSeries(priceResult, epsEntries, years.value)

    if (dailyPeData.length === 0) {
      ElMessage.error('无法计算出有效的 PE 数据，请检查 EPS 数据是否覆盖价格数据的时间段')
      return
    }

    chartData.value = dailyPeData

    // 5. 渲染图表
    renderChart()
    ElMessage.success(`分析完成！共 ${dailyPeData.length} 个有效交易日数据`)

  } catch (error) {
    ElMessage.error(`数据获取失败: ${error.message || '请检查网络和 API Key'}`)
    console.error(error)
  } finally {
    loading.value = false
  }
}

// ==================== ECharts 可视化 ====================
function renderChart() {
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartRef.value)
  }

  const dates = chartData.value.map(d => d.date)
  const peValues = chartData.value.map(d => d.pe)

  // 计算各分位值
  const sorted = [...peValues].sort((a, b) => a - b)
  const n = sorted.length
  const p5 = sorted[Math.floor(n * 0.05)]
  const p10 = sorted[Math.floor(n * 0.10)]
  const p25 = sorted[Math.floor(n * 0.25)]
  const p50 = sorted[Math.floor(n * 0.50)]
  const p75 = sorted[Math.floor(n * 0.75)]
  const p90 = sorted[Math.floor(n * 0.90)]
  const p95 = sorted[Math.floor(n * 0.95)]
  const cur = currentPe.value

  const option = {
    backgroundColor: '#ffffff',
    title: {
      text: `${symbol.value} P/E Ratio (TTM) — 近 ${years.value} 年`,
      left: 'center',
      top: 5,
      textStyle: { fontSize: 16, fontWeight: 600 },
    },
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        const d = params[0]
        const raw = chartData.value[d.dataIndex]
        const quarters = raw ? raw.usedQuarters.join(' + ') : ''
        return `
          <div style="font-size:12px">
            <strong>${d.axisValue}</strong><br/>
            PE(TTM): <strong style="color:#1f77b4">${d.value.toFixed(2)}</strong><br/>
            收盘价: $${raw ? raw.price.toFixed(2) : '-'}<br/>
            TTM EPS: $${raw ? raw.ttmEps.toFixed(4) : '-'}<br/>
            <span style="color:#888">分母: ${quarters}</span>
          </div>
        `
      },
    },
    legend: {
      data: ['PE(TTM)', '10%分位', '50%分位', '90%分位', '当前'],
      top: 40,
    },
    grid: {
      left: '6%',
      right: '8%',
      top: 90,
      bottom: '12%',
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLabel: {
        rotate: 30,
        fontSize: 10,
        formatter(val) {
          // 只显示每月第一个交易日，避免标签过密
          return val
        },
      },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: {
        formatter: val => val.toFixed(0),
      },
      splitLine: { lineStyle: { color: '#f0f0f0' } },
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        filterMode: 'none',
      },
      {
        type: 'slider',
        xAxisIndex: 0,
        bottom: 20,
        height: 25,
        fillerColor: 'rgba(100,149,237,0.1)',
        borderColor: '#ddd',
      },
    ],
    series: [
      // PE 折线
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
          label: {
            fontSize: 11,
            position: 'insideEndTop',
          },
          data: [
            {
              yAxis: p10,
              name: `10% (${p10.toFixed(1)})`,
              lineStyle: { color: '#52c41a', type: 'dashed' },
              label: { formatter: `10% (${p10.toFixed(1)})`, color: '#52c41a' },
            },
            {
              yAxis: p50,
              name: `50% (${p50.toFixed(1)})`,
              lineStyle: { color: '#faad14', type: 'dashed' },
              label: { formatter: `50% (${p50.toFixed(1)})`, color: '#faad14' },
            },
            {
              yAxis: p90,
              name: `90% (${p90.toFixed(1)})`,
              lineStyle: { color: '#f5222d', type: 'dashed' },
              label: { formatter: `90% (${p90.toFixed(1)})`, color: '#f5222d' },
            },
            {
              yAxis: cur,
              name: `当前 (${cur.toFixed(1)})`,
              lineStyle: { color: '#722ed1', type: 'solid', width: 2 },
              label: { formatter: `当前 (${cur.toFixed(1)})`, color: '#722ed1' },
            },
          ],
        },
        markArea: {
          silent: true,
          data: [
            // 10%~50% 低估区间
            [{ yAxis: p10, itemStyle: { color: 'rgba(82,196,26,0.06)' } }, { yAxis: p50 }],
            // 50%~90% 高估区间
            [{ yAxis: p50, itemStyle: { color: 'rgba(250,173,20,0.06)' } }, { yAxis: p90 }],
            // 90%以上极度高估
            [{ yAxis: p90, itemStyle: { color: 'rgba(245,34,45,0.08)' } }, { yAxis: sorted[n - 1] + 5 }],
          ],
        },
      },
    ],
  }

  chartInstance.value.setOption(option, true)
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadFromStorage()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance.value?.dispose()
  chartInstance.value = null
})

function handleResize() {
  chartInstance.value?.resize()
}
</script>

<style scoped>
.pe-analyzer {
  max-width: 1200px;
  margin: 2px auto;
  padding: 0 4px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.controls-row {
  margin-bottom: 16px;
}

/* ===== 汇总卡片 ===== */
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

/* ===== 图表 ===== */
.chart-container {
  width: 100%;
  height: 520px;
  margin: 10px 0;
}
</style>
