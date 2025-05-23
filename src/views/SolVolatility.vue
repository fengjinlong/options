<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue";
import axios from "axios";
import * as echarts from "echarts";

// 添加节流函数
const throttle = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let lastTime = 0;
  return function (this: any, ...args: Parameters<T>): void {
    const now = Date.now();
    if (now - lastTime >= delay) {
      fn.apply(this, args);
      lastTime = now;
    }
  };
};

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

// 添加当前高亮的点索引记录
const currentHighlightIndex = ref({
  solana: -1,
  bitcoin: -1,
});

// 获取历史价格数据
const fetchPriceData = async (coin: string, days: number) => {
  const coinKey = coin as "solana" | "bitcoin";
  loading.value[coinKey] = true;
  error.value[coinKey] = null;

  try {
    console.log(`Fetching ${coin} data for ${days} days...`);

    // 多获取30天数据以便计算波动率
    const requestDays = days + 30;

    const response = await axios.get(
      `https://api.coingecko.com/api/v3/coins/${coin}/market_chart`,
      {
        params: {
          vs_currency: "usd",
          days: requestDays,
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

    // 使用30天的滚动窗口计算波动率
    const window = 30;
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

      // 使用正确的价格索引，因为prices数组比logReturns多一个元素
      const date = new Date(prices[i + 1][0]);
      const dateStr = date.toISOString().split("T")[0];
      const price = prices[i + 1][1];

      volatilities.push({
        date: dateStr,
        value: parseFloat(annualizedVol.toFixed(2)),
        price: parseFloat(price.toFixed(2)),
      });
    }

    // 只保留最后days天的数据，确保与用户选择的时间范围匹配
    const trimmedData = volatilities.slice(-days);

    volatilityData.value[coinKey] = trimmedData;
    console.log(
      `Processed ${coinKey} data: ${trimmedData.length} days from ${
        trimmedData[0].date
      } to ${trimmedData[trimmedData.length - 1].date}`
    );

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
          axisPointer: {
            show: true,
            snap: true,
            label: {
              show: true,
              formatter: "{value}%",
            },
            lineStyle: {
              color: "#FF0000",
              width: 1,
            },
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
      axisPointer: {
        link: [{ xAxisIndex: "all" }],
        show: true,
        type: "line",
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

    // 优化的鼠标移动处理函数
    const handleMouseMove = throttle((e: MouseEvent) => {
      if (!chartRef.value || !charts.value[coinKey]) return;

      const rect = chartRef.value.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      try {
        const pointInGrid = charts.value[coinKey]!.containPixel("grid", [x, y]);
        if (pointInGrid) {
          // 获取X轴日期索引
          const xIndex = Math.round(
            charts.value[coinKey]!.convertFromPixel({ xAxisIndex: 0 }, x)
          );

          // 确保索引有效且与当前高亮的点不同
          if (
            xIndex >= 0 &&
            xIndex < data.length &&
            xIndex !== currentHighlightIndex.value[coinKey]
          ) {
            const item = data[xIndex];

            // 计算提示框位置，确保不会超出容器
            let tooltipX = x;
            let tooltipY = y - 80; // 向上偏移

            // 获取容器宽度
            const containerWidth = chartRef.value.clientWidth;

            // 如果靠近右边，将提示框向左偏移
            if (x > containerWidth - 200) {
              tooltipX = containerWidth - 200;
            }

            // 如果靠近顶部，将提示框向下偏移
            if (tooltipY < 10) {
              tooltipY = 10;
            }

            // 更新提示框信息
            customTooltip.value[coinKey] = {
              show: true,
              x: tooltipX,
              y: tooltipY,
              date: item.date,
              volatility: item.value,
              price: item.price,
            };

            // 如果之前有高亮的点，先取消高亮
            if (currentHighlightIndex.value[coinKey] !== -1) {
              charts.value[coinKey]!.dispatchAction({
                type: "downplay",
                seriesIndex: [0, 1],
                dataIndex: currentHighlightIndex.value[coinKey],
              });
            }

            // 高亮新的点
            charts.value[coinKey]!.dispatchAction({
              type: "highlight",
              seriesIndex: [0, 1],
              dataIndex: xIndex,
            });

            // 更新当前高亮的点索引
            currentHighlightIndex.value[coinKey] = xIndex;
          }
        } else if (currentHighlightIndex.value[coinKey] !== -1) {
          // 鼠标移出图表区域时，取消高亮并重置索引
          customTooltip.value[coinKey].show = false;
          charts.value[coinKey]!.dispatchAction({
            type: "downplay",
            seriesIndex: [0, 1],
            dataIndex: currentHighlightIndex.value[coinKey],
          });
          currentHighlightIndex.value[coinKey] = -1;
        }
      } catch (e) {
        console.error(`Error in mousemove handler:`, e);
        customTooltip.value[coinKey].show = false;
      }
    }, 50); // 50ms的节流时间

    const handleMouseLeave = () => {
      if (currentHighlightIndex.value[coinKey] !== -1) {
        customTooltip.value[coinKey].show = false;
        // 取消高亮
        if (charts.value[coinKey]) {
          charts.value[coinKey]!.dispatchAction({
            type: "downplay",
            seriesIndex: [0, 1],
            dataIndex: currentHighlightIndex.value[coinKey],
          });
        }
        currentHighlightIndex.value[coinKey] = -1;
      }
    };

    // 修改移动设备上的触摸事件处理
    const handleTouchMove = throttle((e: TouchEvent) => {
      e.preventDefault();
      if (e.touches.length > 0 && chartRef.value) {
        const touch = e.touches[0];
        const rect = chartRef.value.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;

        try {
          const pointInGrid = charts.value[coinKey]!.containPixel("grid", [
            x,
            y,
          ]);
          if (pointInGrid) {
            const xIndex = Math.round(
              charts.value[coinKey]!.convertFromPixel({ xAxisIndex: 0 }, x)
            );

            if (
              xIndex >= 0 &&
              xIndex < data.length &&
              xIndex !== currentHighlightIndex.value[coinKey]
            ) {
              const item = data[xIndex];

              let tooltipX = Math.min(x, chartRef.value.clientWidth - 230);
              tooltipX = Math.max(10, tooltipX);
              let tooltipY = y;

              customTooltip.value[coinKey] = {
                show: true,
                x: tooltipX,
                y: tooltipY,
                date: item.date,
                volatility: item.value,
                price: item.price,
              };

              if (currentHighlightIndex.value[coinKey] !== -1) {
                charts.value[coinKey]!.dispatchAction({
                  type: "downplay",
                  seriesIndex: [0, 1],
                  dataIndex: currentHighlightIndex.value[coinKey],
                });
              }

              charts.value[coinKey]!.dispatchAction({
                type: "highlight",
                seriesIndex: [0, 1],
                dataIndex: xIndex,
              });

              currentHighlightIndex.value[coinKey] = xIndex;
            }
          }
        } catch (e) {
          console.error(`Error in touchmove handler:`, e);
        }
      }
    }, 50);

    // 安全添加事件监听
    if (chartRef.value) {
      chartRef.value.addEventListener("mousemove", handleMouseMove);
      chartRef.value.addEventListener("mouseleave", handleMouseLeave);
      chartRef.value.addEventListener("touchmove", handleTouchMove);
      chartRef.value.addEventListener("touchend", () => {
        setTimeout(() => {
          handleMouseLeave();
        }, 500);
      });
    }

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

  console.log(`Time window changed to ${days} days`);

  // 清空当前数据，显示加载状态
  volatilityData.value.solana = [];
  volatilityData.value.bitcoin = [];

  fetchPriceData("solana", timeWindow.value);
  fetchPriceData("bitcoin", timeWindow.value);
};

// 辅助函数：格式化日期显示
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("zh-CN");
};

// 获取日期范围
const getDateRange = (coinKey: "solana" | "bitcoin") => {
  const data = volatilityData.value[coinKey];
  if (!data || data.length === 0) return "暂无数据";

  const startDate = formatDate(data[0].date);
  const endDate = formatDate(data[data.length - 1].date);

  return `${startDate} 至 ${endDate}`;
};

const solanaDateRange = computed(() => getDateRange("solana"));
const bitcoinDateRange = computed(() => getDateRange("bitcoin"));

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
    <div class="page-header">
      <h1>coingecko 历史波动率分析</h1>
    </div>
    <div class="time-selector">
      <el-radio-group v-model="timeWindow" @change="changeTimeWindow">
        <el-radio-button :label="30">30天</el-radio-button>
        <el-radio-button :label="60">60天</el-radio-button>
        <el-radio-button :label="90">90天</el-radio-button>
        <el-radio-button :label="180">180天</el-radio-button>
        <!-- <el-radio-button :label="365">1年</el-radio-button> -->
      </el-radio-group>
    </div>

    <div class="charts-grid">
      <!-- SOL Chart -->
      <div class="chart-section">
        <h2>SOL 历史波动率分析</h2>
        <p v-if="!loading.solana && !error.solana" class="date-range">
          {{ solanaDateRange }}
        </p>
        <div v-if="loading.solana" class="loading-container">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error.solana" class="error-message">
          <el-alert :title="error.solana" type="error" />
        </div>
        <div v-else class="chart-container" style="position: relative">
          <div class="chart-div" ref="solanaChartRef"></div>
          <!-- 自定义提示框 -->
          <div
            v-if="customTooltip.solana.show"
            class="custom-tooltip"
            :style="{
              left: `${customTooltip.solana.x}px`,
              top: `${customTooltip.solana.y}px`,
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
        <p v-if="!loading.bitcoin && !error.bitcoin" class="date-range">
          {{ bitcoinDateRange }}
        </p>
        <div v-if="loading.bitcoin" class="loading-container">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error.bitcoin" class="error-message">
          <el-alert :title="error.bitcoin" type="error" />
        </div>
        <div v-else class="chart-container" style="position: relative">
          <div class="chart-div" ref="bitcoinChartRef"></div>
          <!-- 自定义提示框 -->
          <div
            v-if="customTooltip.bitcoin.show"
            class="custom-tooltip"
            :style="{
              left: `${customTooltip.bitcoin.x}px`,
              top: `${customTooltip.bitcoin.y}px`,
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
  background-color: rgba(255, 255, 255, 0.98);
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  min-width: 180px;
  pointer-events: none;
  transform: translate(10px, -50%);
  max-width: 220px;
}

.tooltip-date {
  font-weight: bold;
  margin-bottom: 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
  color: #333;
  font-size: 14px;
}

.tooltip-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.tooltip-price {
  font-weight: 500;
  color: #2c3e50;
}

.date-range {
  text-align: center;
  margin-top: -15px;
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
