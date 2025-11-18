<template>
  <div class="exchange-flow-dashboard">
    <div class="dashboard-header">
      <h1>交易所资金流向分析仪表盘</h1>
    </div>

    <div class="dashboard-container">
      <!-- 输入区域 -->
      <div class="input-section">
        <el-card class="input-card">
          <template #header>
            <div class="card-header">数据输入</div>
          </template>
          <div class="input-grid">
            <div class="input-item">
              <label>BTC 24h USD 流量 (USD)</label>
              <el-input
                v-model.number="inputs.btcUsdFlow"
                type="number"
                placeholder="正值=净流入，负值=净流出"
                clearable
              />
            </div>
            <div class="input-item">
              <label>USDT 24h USD 流量 (USD)</label>
              <el-input
                v-model.number="inputs.usdtUsdFlow"
                type="number"
                placeholder="输入 USDT 流量"
                clearable
              />
            </div>
            <div class="input-item">
              <label>USDC 24h USD 流量 (USD)</label>
              <el-input
                v-model.number="inputs.usdcUsdFlow"
                type="number"
                placeholder="输入 USDC 流量"
                clearable
              />
            </div>
            <div class="input-item">
              <label>BTC 当前价格 (USD/BTC)</label>
              <el-input
                v-model.number="inputs.btcPrice"
                type="number"
                placeholder="输入 BTC 价格"
                clearable
              />
            </div>
            <div class="input-item">
              <label>BTC Exchange Reserve 趋势</label>
              <el-select
                v-model="inputs.btcReserveTrend"
                placeholder="选择趋势"
                clearable
              >
                <el-option label="上升" value="上升" />
                <el-option label="下降" value="下降" />
                <el-option label="横盘" value="横盘" />
              </el-select>
            </div>
            <div class="input-item">
              <label>Stablecoin Exchange Reserves 趋势</label>
              <el-select
                v-model="inputs.stablecoinReserveTrend"
                placeholder="选择趋势"
                clearable
              >
                <el-option label="上升" value="上升" />
                <el-option label="下降" value="下降" />
                <el-option label="横盘" value="横盘" />
              </el-select>
            </div>
          </div>
          <div class="calculate-button-container">
            <el-button type="primary" size="large" @click="calculate"
              >计算</el-button
            >
          </div>
        </el-card>
      </div>

      <!-- 计算结果区域 -->
      <div class="results-section">
        <!-- 计算值 -->
        <el-card class="calc-card">
          <template #header>
            <div class="card-header">计算结果</div>
          </template>
          <div class="calc-grid">
            <div class="calc-item">
              <div class="calc-label">BTC 24h Netflow (BTC)</div>
              <div class="calc-value">{{ formatNumber(btcNetflow) }} BTC</div>
            </div>
            <div class="calc-item">
              <div class="calc-label">稳定币 24h 总净流量 (USD)</div>
              <div class="calc-value">
                {{ formatCurrency(stablecoinNetflow) }}
              </div>
            </div>
            <div class="calc-item">
              <div class="calc-label">稳定币 24h Netflow (BTC 等价)</div>
              <div class="calc-value">
                {{ formatNumber(stablecoinNetflowBtc) }} BTC
              </div>
            </div>
          </div>
        </el-card>

        <!-- 评分卡片 -->
        <div class="scores-grid">
          <el-card class="score-card">
            <div class="score-label">BTC 短期评分</div>
            <div class="score-value" :class="getScoreClass(btcScore)">
              {{ btcScore }}
            </div>
          </el-card>
          <el-card class="score-card">
            <div class="score-label">稳定币短期评分</div>
            <div class="score-value" :class="getScoreClass(stablecoinScore)">
              {{ stablecoinScore }}
            </div>
          </el-card>
          <el-card class="score-card">
            <div class="score-label">BTC Exchange Reserve 分数</div>
            <div class="score-value" :class="getScoreClass(btcReserveScore)">
              {{ btcReserveScore }}
            </div>
          </el-card>
          <el-card class="score-card">
            <div class="score-label">Stablecoin Exchange Reserve 分数</div>
            <div
              class="score-value"
              :class="getScoreClass(stablecoinReserveScore)"
            >
              {{ stablecoinReserveScore }}
            </div>
          </el-card>
        </div>

        <!-- 总分和市场状态 -->
        <el-card class="status-card" :class="marketStatusClass">
          <div class="status-content">
            <div class="total-score-section">
              <div class="total-score-label">总分 (TOTAL_SCORE)</div>
              <div class="total-score-value">{{ totalScore }}</div>
            </div>
            <div class="market-status-section">
              <div class="market-status-label">市场状态</div>
              <div class="market-status-value">{{ marketStatus }}</div>
            </div>
            <div class="recommendation-section">
              <div class="recommendation-label">操作建议</div>
              <div class="recommendation-value">{{ recommendation }}</div>
            </div>
          </div>
        </el-card>

        <!-- 图表 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">评分可视化</div>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import * as echarts from "echarts";

// 输入数据
const inputs = ref({
  btcUsdFlow: null as number | null,
  usdtUsdFlow: null as number | null,
  usdcUsdFlow: null as number | null,
  btcPrice: null as number | null,
  btcReserveTrend: null as string | null,
  stablecoinReserveTrend: null as string | null,
});

// 计算结果（使用 ref 而不是 computed）
const btcNetflow = ref(0);
const stablecoinNetflow = ref(0);
const stablecoinNetflowBtc = ref(0);
const btcScore = ref(0);
const stablecoinScore = ref(0);
const btcReserveScore = ref(0);
const stablecoinReserveScore = ref(0);
const totalScore = ref(0);
const marketStatus = ref("等待数据");
const recommendation = ref("请点击计算按钮");

// 市场状态样式类
const marketStatusClass = computed(() => {
  const status = marketStatus.value;
  return {
    "status-strong-bull": status === "强多",
    "status-weak-bull": status === "弱多",
    "status-neutral": status === "中性",
    "status-weak-bear": status === "弱空",
    "status-strong-bear": status === "强空",
  };
});

// 计算函数
const calculate = () => {
  // 计算 BTC Netflow
  if (
    inputs.value.btcUsdFlow !== null &&
    inputs.value.btcPrice !== null &&
    inputs.value.btcPrice !== 0
  ) {
    btcNetflow.value = inputs.value.btcUsdFlow / inputs.value.btcPrice;
  } else {
    btcNetflow.value = 0;
  }

  // 计算稳定币净流量
  const usdt = inputs.value.usdtUsdFlow ?? 0;
  const usdc = inputs.value.usdcUsdFlow ?? 0;
  stablecoinNetflow.value = usdt + usdc;

  // 计算稳定币净流量（BTC 等价）
  if (inputs.value.btcPrice !== null && inputs.value.btcPrice !== 0) {
    stablecoinNetflowBtc.value =
      stablecoinNetflow.value / inputs.value.btcPrice;
  } else {
    stablecoinNetflowBtc.value = 0;
  }

  // 计算 BTC 短期评分
  const netflow = btcNetflow.value;
  if (netflow <= -4000) {
    btcScore.value = 2;
  } else if (netflow <= -1000) {
    btcScore.value = 1;
  } else if (netflow <= 1000) {
    btcScore.value = 0;
  } else if (netflow <= 4000) {
    btcScore.value = -1;
  } else {
    btcScore.value = -2;
  }

  // 计算稳定币短期评分
  const stableNetflow = stablecoinNetflow.value;
  if (stableNetflow >= 200000000) {
    stablecoinScore.value = 2; // 2亿
  } else if (stableNetflow >= 50000000) {
    stablecoinScore.value = 1; // 5000万
  } else if (stableNetflow >= -50000000) {
    stablecoinScore.value = 0; // -5000万
  } else if (stableNetflow >= -200000000) {
    stablecoinScore.value = -1; // -2亿
  } else {
    stablecoinScore.value = -2;
  }

  // 计算 BTC Exchange Reserve 分数
  const btcTrend = inputs.value.btcReserveTrend;
  if (btcTrend === "下降") {
    btcReserveScore.value = 1;
  } else if (btcTrend === "横盘") {
    btcReserveScore.value = 0;
  } else if (btcTrend === "上升") {
    btcReserveScore.value = -1;
  } else {
    btcReserveScore.value = 0;
  }

  // 计算 Stablecoin Exchange Reserve 分数
  const stableTrend = inputs.value.stablecoinReserveTrend;
  if (stableTrend === "上升") {
    stablecoinReserveScore.value = 1;
  } else if (stableTrend === "横盘") {
    stablecoinReserveScore.value = 0;
  } else if (stableTrend === "下降") {
    stablecoinReserveScore.value = -1;
  } else {
    stablecoinReserveScore.value = 0;
  }

  // 计算总分
  totalScore.value =
    btcScore.value +
    stablecoinScore.value +
    btcReserveScore.value +
    stablecoinReserveScore.value;

  // 计算市场状态
  const score = totalScore.value;
  if (score >= 3) {
    marketStatus.value = "强多";
  } else if (score >= 1) {
    marketStatus.value = "弱多";
  } else if (score === 0) {
    marketStatus.value = "中性";
  } else if (score >= -2) {
    marketStatus.value = "弱空";
  } else {
    marketStatus.value = "强空";
  }

  // 计算操作建议
  const status = marketStatus.value;
  const recommendations: Record<string, string> = {
    强多: "趋势多单 / 回调买入",
    弱多: "轻仓做多 / 避免开空",
    中性: "等待方向 / 区间震荡",
    弱空: "轻仓空 / 不追多",
    强空: "趋势空 / 避开多单",
  };
  recommendation.value = recommendations[status] || "等待数据";

  // 更新图表
  nextTick(() => {
    updateChart();
  });
};

// 工具函数
const formatNumber = (num: number): string => {
  if (num === 0 || isNaN(num)) return "0";
  return num.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const formatCurrency = (num: number): string => {
  if (num === 0 || isNaN(num)) return "$0";
  if (Math.abs(num) >= 100000000) {
    return `$${(num / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(num) >= 10000) {
    return `$${(num / 10000).toFixed(2)}万`;
  }
  return `$${num.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const getScoreClass = (score: number): string => {
  if (score >= 2) return "score-positive-strong";
  if (score === 1) return "score-positive-weak";
  if (score === 0) return "score-neutral";
  if (score === -1) return "score-negative-weak";
  return "score-negative-strong";
};

// 图表
const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const updateChart = () => {
  if (!chartRef.value) return;

  const scores = [
    { name: "BTC短期", value: btcScore.value },
    { name: "稳定币短期", value: stablecoinScore.value },
    { name: "BTC储备", value: btcReserveScore.value },
    { name: "稳定币储备", value: stablecoinReserveScore.value },
  ];

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: scores.map((s) => s.name),
      axisLabel: {
        rotate: 0,
      },
    },
    yAxis: {
      type: "value",
      min: -2,
      max: 2,
      interval: 1,
    },
    series: [
      {
        name: "评分",
        type: "bar",
        data: scores.map((s) => ({
          value: s.value,
          itemStyle: {
            color:
              s.value >= 2
                ? "#67C23A"
                : s.value === 1
                ? "#95D475"
                : s.value === 0
                ? "#909399"
                : s.value === -1
                ? "#F56C6C"
                : "#F56C6C",
          },
        })),
        label: {
          show: true,
          position: "top",
          formatter: "{c}",
        },
      },
    ],
  };

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  chartInstance.setOption(option);
};

onMounted(() => {
  nextTick(() => {
    // 初始化图表（不显示数据，等待用户点击计算）
    if (chartRef.value) {
      chartInstance = echarts.init(chartRef.value);
      // 响应式调整
      window.addEventListener("resize", () => {
        chartInstance?.resize();
      });
    }
  });
});
</script>

<style scoped>
.exchange-flow-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0;
}

.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section,
.results-section {
  width: 100%;
}

.input-card,
.calc-card,
.status-card,
.chart-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.input-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-item label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.calculate-button-container {
  margin-top: 20px;
  text-align: center;
  padding: 10px 0;
}

.calc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.calc-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.calc-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.calc-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.score-card {
  text-align: center;
  padding: 20px;
}

.score-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.score-value {
  font-size: 36px;
  font-weight: 700;
  transition: all 0.3s;
}

.score-positive-strong {
  color: #67c23a;
}

.score-positive-weak {
  color: #95d475;
}

.score-neutral {
  color: #909399;
}

.score-negative-weak {
  color: #f56c6c;
}

.score-negative-strong {
  color: #f56c6c;
}

.status-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.status-strong-bull {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.status-weak-bull {
  background: linear-gradient(135deg, #95d475 0%, #b3e19d 100%);
  color: white;
}

.status-neutral {
  background: linear-gradient(135deg, #909399 0%, #b1b3b8 100%);
  color: white;
}

.status-weak-bear {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  color: white;
}

.status-strong-bear {
  background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
  color: white;
}

.status-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  text-align: center;
}

.total-score-section,
.market-status-section,
.recommendation-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.total-score-label,
.market-status-label,
.recommendation-label {
  font-size: 14px;
  opacity: 0.9;
}

.total-score-value {
  font-size: 48px;
  font-weight: 700;
}

.market-status-value {
  font-size: 32px;
  font-weight: 700;
}

.recommendation-value {
  font-size: 18px;
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .exchange-flow-dashboard {
    padding: 10px;
  }

  .dashboard-header h1 {
    font-size: 22px;
  }

  .input-grid {
    grid-template-columns: 1fr;
  }

  .calc-grid {
    grid-template-columns: 1fr;
  }

  .scores-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .status-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .chart-container {
    height: 300px;
  }
}

@media (max-width: 480px) {
  .scores-grid {
    grid-template-columns: 1fr;
  }

  .total-score-value {
    font-size: 36px;
  }

  .market-status-value {
    font-size: 24px;
  }
}
</style>
