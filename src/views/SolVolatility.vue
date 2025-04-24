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
const customTooltip = ref({
  solana: { show: false, x: 0, y: 0, date: "", volatility: 0, price: 0 },
  bitcoin: { show: false, x: 0, y: 0, date: "", volatility: 0, price: 0 },
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
        timeout: 15000,
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

    if (prices.length < 2) {
      throw new Error(`Insufficient data points for ${coin}: ${prices.length}`);
    }

    const logReturns = [];
    for (let i = 1; i < prices.length; i++) {
      const previousPrice = prices[i - 1][1];
      const currentPrice = prices[i][1];
      if (
        typeof previousPrice !== "number" ||
        typeof currentPrice !== "number" ||
        previousPrice <= 0 ||
        currentPrice <= 0
      ) {
        console.warn(
          `Invalid price data at index ${i}:`,
          previousPrice,
          currentPrice
        );
        continue;
      }
      logReturns.push(Math.log(currentPrice / previousPrice));
    }

    if (logReturns.length === 0) {
      throw new Error(`No valid returns calculated for ${coin}`);
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

    // 延迟初始化图表，确保DOM已经准备好
    setTimeout(() => {
      initChart(coinKey);
    }, 200);
  } catch (err) {
    console.error(`Failed to fetch ${coin} price data:`, err);
    error.value[coinKey] = `获取数据失败：${
      err instanceof Error ? err.message : "未知错误"
    }`;
    loading.value[coinKey] = false;
  }
};

// 初始化ECharts图表
const initChart = (coinKey: "solana" | "bitcoin") => {
  const chartRef = coinKey === "solana" ? solanaChartRef : bitcoinChartRef;

  console.log(`Initializing ${coinKey} chart`);
  if (!chartRef.value) {
    console.error(`${coinKey} chart container not found`);
    return;
  }

  if (charts.value[coinKey]) {
    try {
      charts.value[coinKey]!.dispose();
    } catch (e) {
      console.error(`Error disposing chart:`, e);
    }
    charts.value[coinKey] = null;
  }

  try {
    charts.value[coinKey] = echarts.init(chartRef.value);

    const data = volatilityData.value[coinKey];
    if (!data || data.length === 0) {
      console.error(`No data available for ${coinKey}`);
      return;
    }

    // 准备最基本的图表数据
    const dates = data.map((item) => item.date);
    const values = data.map((item) => item.value);
    const prices = data.map((item) => item.price);

    // 基本图表配置，不使用echarts内置tooltip
    const option = {
      grid: {
        left: "10%",
        right: "10%",
        bottom: "15%",
        top: "15%",
      },
      xAxis: {
        type: "category",
        data: dates,
        axisPointer: {
          show: true,
        },
      },
      yAxis: [
        {
          type: "value",
          name: "波动率",
          axisLabel: {
            formatter: "{value}%",
          },
        },
        {
          type: "value",
          name: "价格",
          position: "right",
          axisLabel: {
            formatter: "${value}",
          },
        },
      ],
      toolbox: {
        show: true,
        feature: {
          dataZoom: {
            yAxisIndex: "none",
          },
          restore: {},
        },
      },
      dataZoom: [
        {
          type: "inside",
          start: 0,
          end: 100,
        },
      ],
      series: [
        {
          name: "波动率",
          type: "line",
          data: values,
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          emphasis: {
            itemStyle: {
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
          },
          itemStyle: {
            color: "#00C853",
          },
        },
        {
          name: "价格",
          type: "line",
          yAxisIndex: 1,
          data: prices,
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          emphasis: {
            itemStyle: {
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
          },
          itemStyle: {
            color: coinKey === "solana" ? "#9945ff" : "#F7931A",
          },
        },
      ],
    };

    // 设置图表选项
    charts.value[coinKey]!.setOption(option);

    // 添加自定义鼠标事件处理
    chartRef.value.addEventListener("mousemove", (e: MouseEvent) => {
      const rect = chartRef.value!.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      try {
        if (!charts.value[coinKey]) return;

        const pointInGrid = charts.value[coinKey]!.containPixel("grid", [x, y]);
        if (pointInGrid) {
          // 获取X轴日期索引
          const xIndex = Math.round(
            charts.value[coinKey]!.convertFromPixel({ xAxisIndex: 0 }, x)
          );

          // 确保索引有效
          if (xIndex >= 0 && xIndex < data.length) {
            const item = data[xIndex];

            // 更新提示框信息
            customTooltip.value[coinKey] = {
              show: true,
              x: x,
              y: y,
              date: item.date,
              volatility: item.value,
              price: item.price,
            };

            // 高亮对应的点
            charts.value[coinKey]!.dispatchAction({
              type: "highlight",
              seriesIndex: [0, 1],
              dataIndex: xIndex,
            });
          }
        } else {
          customTooltip.value[coinKey].show = false;

          // 取消高亮
          charts.value[coinKey]!.dispatchAction({
            type: "downplay",
            seriesIndex: [0, 1],
          });
        }
      } catch (e) {
        console.error(`Error in mousemove handler:`, e);
        customTooltip.value[coinKey].show = false;
      }
    });

    chartRef.value.addEventListener("mouseleave", () => {
      customTooltip.value[coinKey].show = false;

      // 取消高亮
      if (charts.value[coinKey]) {
        charts.value[coinKey]!.dispatchAction({
          type: "downplay",
          seriesIndex: [0, 1],
        });
      }
    });

    // 添加触摸事件支持
    chartRef.value.addEventListener("touchmove", (e: TouchEvent) => {
      e.preventDefault();
      if (e.touches.length > 0) {
        const touch = e.touches[0];
        const rect = chartRef.value!.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;

        // 复用与鼠标移动相同的处理逻辑
        try {
          if (!charts.value[coinKey]) return;

          const pointInGrid = charts.value[coinKey]!.containPixel("grid", [
            x,
            y,
          ]);
          if (pointInGrid) {
            // 获取X轴日期索引
            const xIndex = Math.round(
              charts.value[coinKey]!.convertFromPixel({ xAxisIndex: 0 }, x)
            );

            // 确保索引有效
            if (xIndex >= 0 && xIndex < data.length) {
              const item = data[xIndex];

              // 更新提示框信息
              customTooltip.value[coinKey] = {
                show: true,
                x: x,
                y: y,
                date: item.date,
                volatility: item.value,
                price: item.price,
              };

              charts.value[coinKey]!.dispatchAction({
                type: "highlight",
                seriesIndex: [0, 1],
                dataIndex: xIndex,
              });
            }
          }
        } catch (e) {
          console.error(`Error in touchmove handler:`, e);
        }
      }
    });

    chartRef.value.addEventListener("touchend", () => {
      setTimeout(() => {
        customTooltip.value[coinKey].show = false;
        if (charts.value[coinKey]) {
          charts.value[coinKey]!.dispatchAction({
            type: "downplay",
            seriesIndex: [0, 1],
          });
        }
      }, 500); // 延迟半秒关闭提示框，让用户有时间查看
    });

    console.log(`${coinKey} chart initialized successfully`);
  } catch (e) {
    console.error(`Failed to initialize ${coinKey} chart:`, e);
    error.value[coinKey] = `图表初始化失败：${
      e instanceof Error ? e.message : "未知错误"
    }`;
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
          <!-- 自定义提示框 -->
          <div
            v-if="customTooltip.solana.show"
            class="custom-tooltip"
            :style="{
              left: `${customTooltip.solana.x}px`,
              top: `${customTooltip.solana.y - 80}px`,
            }"
          >
            <div class="tooltip-date">{{ customTooltip.solana.date }}</div>
            <div class="tooltip-item">
              <span>波动率:</span>
              <span
                :class="getVolatilityClass(customTooltip.solana.volatility)"
              >
                {{ customTooltip.solana.volatility }}% ({{
                  getVolatilityStatus(customTooltip.solana.volatility)
                }})
              </span>
            </div>
            <div class="tooltip-item">
              <span>价格:</span>
              <span class="tooltip-price"
                >${{ customTooltip.solana.price }}</span
              >
            </div>
          </div>
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
          <!-- 自定义提示框 -->
          <div
            v-if="customTooltip.bitcoin.show"
            class="custom-tooltip"
            :style="{
              left: `${customTooltip.bitcoin.x}px`,
              top: `${customTooltip.bitcoin.y - 80}px`,
            }"
          >
            <div class="tooltip-date">{{ customTooltip.bitcoin.date }}</div>
            <div class="tooltip-item">
              <span>波动率:</span>
              <span
                :class="getVolatilityClass(customTooltip.bitcoin.volatility)"
              >
                {{ customTooltip.bitcoin.volatility }}% ({{
                  getVolatilityStatus(customTooltip.bitcoin.volatility)
                }})
              </span>
            </div>
            <div class="tooltip-item">
              <span>价格:</span>
              <span class="tooltip-price"
                >${{ customTooltip.bitcoin.price }}</span
              >
            </div>
          </div>
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

.custom-tooltip {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.95);
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 100;
  min-width: 180px;
  pointer-events: none;
}

.tooltip-date {
  font-weight: bold;
  margin-bottom: 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.tooltip-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.tooltip-price {
  font-weight: 500;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
