<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue";
import axios from "axios";
import * as echarts from "echarts";
import type {
  EChartsTooltipFormatterParams,
  VolatilityDataPoint,
} from "../types/echarts";

// 状态变量
const loading = ref({
  solana: true,
  bitcoin: true,
});
const error = ref<{ solana: string | null; bitcoin: string | null }>({
  solana: null,
  bitcoin: null,
});
const charts = ref({
  solana: null as echarts.ECharts | null,
  bitcoin: null as echarts.ECharts | null,
});
const solanaChartRef = ref<HTMLElement | null>(null);
const bitcoinChartRef = ref<HTMLElement | null>(null);
const timeWindow = ref(30); // 默认30天
const volatilityData = ref({
  solana: [] as { date: string; value: number; price: number }[],
  bitcoin: [] as { date: string; value: number; price: number }[],
});

// 获取历史价格数据
const fetchPriceData = async (coin: string, days: number) => {
  const coinKey = coin as "solana" | "bitcoin";
  loading.value[coinKey] = true;
  error.value[coinKey] = null;

  try {
    console.log(`Fetching ${coin} data for ${days} days...`);
    const response = await axios.get(
      `https://api.coingecko.com/api/v3/coins/${coin}/market_chart`,
      {
        params: {
          vs_currency: "usd",
          days: days,
          interval: "daily",
        },
        timeout: 15000, // 增加超时时间
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      }
    );

    if (
      !response.data ||
      !response.data.prices ||
      response.data.prices.length === 0
    ) {
      throw new Error(`No price data returned for ${coin}`);
    }

    const prices = response.data.prices;
    console.log(`Received ${coin} price data:`, prices.length, "data points");

    const logReturns = [];
    for (let i = 1; i < prices.length; i++) {
      const previousPrice = prices[i - 1][1];
      const currentPrice = prices[i][1];
      logReturns.push(Math.log(currentPrice / previousPrice));
    }

    const window = Math.min(30, logReturns.length);
    const volatilities = [];

    for (let i = window - 1; i < logReturns.length; i++) {
      const windowLogReturns = logReturns.slice(i - window + 1, i + 1);
      const mean =
        windowLogReturns.reduce((a, b) => a + b, 0) / windowLogReturns.length;
      const variance =
        windowLogReturns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) /
        (windowLogReturns.length - 1);
      const stdDev = Math.sqrt(variance);
      const annualizedVol = stdDev * Math.sqrt(365) * 100;

      const date = new Date(prices[i + 1][0]);
      const dateStr = date.toISOString().split("T")[0];
      const price = prices[i + 1][1];

      volatilities.push({
        date: dateStr,
        value: parseFloat(annualizedVol.toFixed(2)),
        price: parseFloat(price.toFixed(2)),
      });
    }

    volatilityData.value[coinKey] = volatilities;
    loading.value[coinKey] = false;

    setTimeout(() => {
      initChart(coinKey);
    }, 100);
  } catch (err) {
    console.error(`Failed to fetch ${coin} price data:`, err);
    error.value[coinKey] = "获取数据失败，请稍后再试";
    loading.value[coinKey] = false;
  }
};

// 初始化ECharts图表
const initChart = (coinKey: "solana" | "bitcoin") => {
  const chartRef = coinKey === "solana" ? solanaChartRef : bitcoinChartRef;

  console.log(`Initializing ${coinKey} chart`);
  if (!chartRef.value) {
    console.error(`${coinKey} chart container not found`);
    setTimeout(() => {
      if (chartRef.value) {
        doInitChart(coinKey);
      } else {
        console.error(`${coinKey} chart container still not found after retry`);
      }
    }, 100);
    return;
  }

  doInitChart(coinKey);
};

// 实际执行图表初始化的函数
const doInitChart = (coinKey: "solana" | "bitcoin") => {
  const chartRef = coinKey === "solana" ? solanaChartRef : bitcoinChartRef;

  if (charts.value[coinKey]) {
    charts.value[coinKey]!.dispose();
  }

  try {
    if (!chartRef.value) {
      console.error(`${coinKey} chart container is not available`);
      return;
    }

    console.log(
      `Initializing ${coinKey} chart with DOM element:`,
      chartRef.value
    );

    charts.value[coinKey] = echarts.init(chartRef.value, null, {
      renderer: "canvas",
    });

    const data = volatilityData.value[coinKey];
    if (!data || data.length === 0) {
      console.error(`No volatility data available for ${coinKey}`);
      return;
    }

    console.log(`${coinKey} data points:`, data.length);

    const dates = data.map((item) => item.date);
    const values = data.map((item) => item.value);
    const prices = data.map((item) => item.price);

    const option = {
      animation: false,
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "cross",
          label: {
            backgroundColor: "#6a7985",
          },
          crossStyle: {
            color: "#999",
            width: 1,
            type: "dashed",
          },
          lineStyle: {
            color: "#999",
            width: 1,
            type: "dashed",
          },
        },
        show: true,
        alwaysShowContent: false, // 设置为true可以强制显示tooltip
        backgroundColor: "rgba(255, 255, 255, 0.95)",
        borderColor: "#ccc",
        borderWidth: 1,
        padding: [10, 15],
        textStyle: {
          color: "#333",
        },
        confine: true,
        extraCssText: "box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);z-index:100;",
        formatter: function (params: any[]) {
          if (!Array.isArray(params) || params.length === 0) return "";

          const date = params[0].axisValue;
          const volatility = params.find(
            (p) => p.seriesName === "波动率"
          )?.value;
          const price = params.find((p) => p.seriesName === "价格")?.value;

          const volatilityStatus =
            typeof volatility === "number"
              ? getVolatilityStatus(volatility)
              : "";

          const volatilityClass =
            typeof volatility === "number"
              ? volatility < 30
                ? "color:#67c23a;"
                : volatility < 50
                ? "color:#e6a23c;"
                : "color:#f56c6c;font-weight:" +
                  (volatility >= 70 ? "bold" : "normal")
              : "";

          return `
            <div style="font-size: 14px;min-width:180px;">
              <div style="margin-bottom: 8px;font-weight:bold;border-bottom:1px solid #eee;padding-bottom:5px;">${date}</div>
              <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span>波动率:</span> 
                <span style="${volatilityClass}">${
            typeof volatility === "number" ? volatility.toFixed(2) : "0"
          }% (${volatilityStatus})</span>
              </div>
              <div style="display:flex;justify-content:space-between;">
                <span>价格:</span>
                <span style="font-weight:500;">$${
                  typeof price === "number" ? price.toLocaleString() : "0"
                }</span>
              </div>
            </div>
          `;
        },
      },
      grid: {
        left: "10%",
        right: "10%",
        bottom: "15%",
        top: "15%",
      },
      xAxis: {
        type: "category",
        data: dates,
      },
      yAxis: [
        {
          type: "value",
          name: "波动率",
          splitLine: { show: true },
        },
        {
          type: "value",
          name: "价格",
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "波动率",
          type: "line",
          data: values,
          symbolSize: 6,
          symbol: "circle",
          smooth: true,
          showSymbol: true,
          emphasis: {
            focus: "series",
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
          },
          itemStyle: {
            color: "#00C853",
          },
          markLine: {
            silent: true,
            lineStyle: {
              color: "#999",
              type: "dashed",
            },
            data: [
              {
                yAxis: values[values.length - 1],
                name: "当前波动率",
              },
            ],
          },
        },
        {
          name: "价格",
          type: "line",
          yAxisIndex: 1,
          data: prices,
          symbolSize: 6,
          symbol: "circle",
          smooth: true,
          showSymbol: true,
          emphasis: {
            focus: "series",
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
          },
          itemStyle: {
            color: coinKey === "solana" ? "#9945ff" : "#F7931A",
          },
          markLine: {
            silent: true,
            lineStyle: {
              color: "#999",
              type: "dashed",
            },
            data: [
              {
                yAxis: prices[prices.length - 1],
                name: "当前价格",
              },
            ],
          },
        },
      ],
    };

    charts.value[coinKey]!.setOption(option);

    // 强制重新渲染并设置事件监听
    charts.value[coinKey]!.resize();

    charts.value[coinKey]!.off("showTip");
    charts.value[coinKey]!.on("showTip", (params) => {
      console.log(`${coinKey} tooltip shown:`, params);
    });

    charts.value[coinKey]!.off("hideTip");
    charts.value[coinKey]!.on("hideTip", (params) => {
      console.log(`${coinKey} tooltip hidden:`, params);
    });

    // 在 doInitChart 函数末尾添加
    setTimeout(() => {
      if (charts.value[coinKey]) {
        try {
          console.log(`Forcing ${coinKey} chart re-render`);
          charts.value[coinKey]!.resize();
          charts.value[coinKey]!.dispatchAction({
            type: "showTip",
            seriesIndex: 0,
            dataIndex: values.length - 1,
          });
          setTimeout(() => {
            if (charts.value[coinKey]) {
              charts.value[coinKey]!.dispatchAction({
                type: "hideTip",
              });
            }
          }, 2000);
        } catch (e) {
          console.error(`Error dispatching chart action: ${e}`);
        }
      }
    }, 500);

    console.log(`${coinKey} chart initialized successfully`);
  } catch (err) {
    console.error(`Error initializing ${coinKey} chart:`, err);
  }
};

// 监听窗口大小变化
window.addEventListener("resize", () => {
  if (charts.value.solana) {
    charts.value.solana.resize();
  }
  if (charts.value.bitcoin) {
    charts.value.bitcoin.resize();
  }
});

// 更改时间窗口
const changeTimeWindow = (days: number) => {
  timeWindow.value = days;
  fetchPriceData("solana", timeWindow.value);
  fetchPriceData("bitcoin", timeWindow.value);
};

// 统计信息
const getStatistics = (coinKey: "solana" | "bitcoin") => {
  const data = volatilityData.value[coinKey];
  if (!data.length) return null;

  const values = data.map((item) => item.value);
  const max = Math.max(...values);
  const maxDate = data[values.indexOf(max)].date;
  const min = Math.min(...values);
  const minDate = data[values.indexOf(min)].date;
  const avg = parseFloat(
    (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
  );
  const current = values[values.length - 1];
  const startDate = data[0].date;
  const endDate = data[data.length - 1].date;

  return {
    max,
    maxDate,
    min,
    minDate,
    avg,
    current,
    startDate,
    endDate,
  };
};

const solanaStats = computed(() => getStatistics("solana"));
const bitcoinStats = computed(() => getStatistics("bitcoin"));

// 获取波动率状态描述
const getVolatilityStatus = (value: number) => {
  if (value < 30) {
    return "低波动率";
  } else if (value < 50) {
    return "中等波动率";
  } else if (value < 70) {
    return "高波动率";
  } else {
    return "极高波动率";
  }
};

// 获取波动率的样式类
const getVolatilityClass = (value: number) => {
  if (value < 30) {
    return "text-success";
  } else if (value < 50) {
    return "text-warning";
  } else if (value < 70) {
    return "text-danger";
  } else {
    return "text-danger bold";
  }
};

// 生命周期钩子
onMounted(async () => {
  console.log(
    "Component mounted - chart refs available:",
    !!solanaChartRef.value,
    !!bitcoinChartRef.value
  );

  await nextTick();
  console.log(
    "After nextTick - chart refs available:",
    !!solanaChartRef.value,
    !!bitcoinChartRef.value
  );

  fetchPriceData("solana", timeWindow.value);
  fetchPriceData("bitcoin", timeWindow.value);
});
</script>

<template>
  <div class="sol-volatility">
    <div class="time-selector">
      <el-radio-group v-model="timeWindow" @change="changeTimeWindow">
        <el-radio-button :label="30">30天</el-radio-button>
        <el-radio-button :label="60">60天</el-radio-button>
        <el-radio-button :label="90">90天</el-radio-button>
        <el-radio-button :label="180">180天</el-radio-button>
        <el-radio-button :label="365">1年</el-radio-button>
      </el-radio-group>
    </div>

    <div class="charts-grid">
      <!-- SOL Chart -->
      <div class="chart-section">
        <h2>SOL 历史波动率分析</h2>
        <div v-if="loading.solana" class="loading-container">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error.solana" class="error-message">
          <el-alert :title="error.solana" type="error" />
        </div>
        <div v-else class="chart-container">
          <div class="chart-div" ref="solanaChartRef"></div>
          <div v-if="solanaStats" class="statistics">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-card shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>SOL 历史波动率指标</span>
                    </div>
                  </template>
                  <el-descriptions border :column="2">
                    <el-descriptions-item label="当前波动率">
                      <span :class="getVolatilityClass(solanaStats.current)">
                        {{ solanaStats.current }}% ({{
                          getVolatilityStatus(solanaStats.current)
                        }})
                      </span>
                    </el-descriptions-item>
                    <el-descriptions-item label="平均波动率">
                      {{ solanaStats.avg }}%
                    </el-descriptions-item>
                    <el-descriptions-item label="最大波动率">
                      <span class="text-danger"
                        >{{ solanaStats.max }}% ({{
                          solanaStats.maxDate
                        }})</span
                      >
                    </el-descriptions-item>
                    <el-descriptions-item label="最小波动率">
                      <span class="text-success"
                        >{{ solanaStats.min }}% ({{
                          solanaStats.minDate
                        }})</span
                      >
                    </el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>

      <!-- BTC Chart -->
      <div class="chart-section">
        <h2>BTC 历史波动率分析</h2>
        <div v-if="loading.bitcoin" class="loading-container">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error.bitcoin" class="error-message">
          <el-alert :title="error.bitcoin" type="error" />
        </div>
        <div v-else class="chart-container">
          <div class="chart-div" ref="bitcoinChartRef"></div>
          <div v-if="bitcoinStats" class="statistics">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-card shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>BTC 历史波动率指标</span>
                    </div>
                  </template>
                  <el-descriptions border :column="2">
                    <el-descriptions-item label="当前波动率">
                      <span :class="getVolatilityClass(bitcoinStats.current)">
                        {{ bitcoinStats.current }}% ({{
                          getVolatilityStatus(bitcoinStats.current)
                        }})
                      </span>
                    </el-descriptions-item>
                    <el-descriptions-item label="平均波动率">
                      {{ bitcoinStats.avg }}%
                    </el-descriptions-item>
                    <el-descriptions-item label="最大波动率">
                      <span class="text-danger"
                        >{{ bitcoinStats.max }}% ({{
                          bitcoinStats.maxDate
                        }})</span
                      >
                    </el-descriptions-item>
                    <el-descriptions-item label="最小波动率">
                      <span class="text-success"
                        >{{ bitcoinStats.min }}% ({{
                          bitcoinStats.minDate
                        }})</span
                      >
                    </el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sol-volatility {
  padding: 20px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.chart-section {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.time-selector {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
  margin-top: 40px;
}

.error-message {
  margin: 40px auto;
  max-width: 500px;
}

.chart-container {
  background-color: white;
  border-radius: 4px;
  padding: 20px;
}

.chart-div {
  width: 100%;
  height: 400px;
}

.statistics {
  margin-top: 30px;
}

.card-header {
  font-weight: bold;
}

.text-success {
  color: #67c23a;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}

.bold {
  font-weight: bold;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
