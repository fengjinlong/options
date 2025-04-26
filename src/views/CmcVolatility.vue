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

// coindesk API Key
// https://developers.coindesk.com/documentation/data-api/index_cc_v1_historical_days

// 添加API配置
const API_CONFIG = {
  BASE_URL: "https://data-api.coindesk.com/index/cc/v1/historical/days",
  INSTRUMENTS: {
    bitcoin: "BTC-USD",
    solana: "SOL-USD",
  },
  DEFAULT_PARAMS: {
    market: "cadli",
    groups: "OHLC",
    aggregate: 1,
    fill: true,
    apply_mapping: true,
    response_format: "JSON",
  },
};

// 定义接口类型
interface PriceDataItem {
  UNIT: "DAY";
  TIMESTAMP: number;
  OPEN: number;
  HIGH: number;
  LOW: number;
  CLOSE: number;
}

// 获取历史价格数据
const fetchPriceData = async (coin: string, days: number) => {
  const coinKey = coin as "solana" | "bitcoin";
  loading.value[coinKey] = true;
  error.value[coinKey] = null;

  try {
    // 为了计算波动率，我们需要额外30天的历史数据
    const requiredDays = days + 30;
    console.log(
      `Fetching ${coin} data for ${requiredDays} days (${days} display days + 30 days for calculation)...`
    );

    const params = new URLSearchParams({
      ...Object.fromEntries(
        Object.entries(API_CONFIG.DEFAULT_PARAMS).map(([key, value]) => [
          key,
          String(value),
        ])
      ),
      instrument: API_CONFIG.INSTRUMENTS[coinKey],
      limit: String(requiredDays), // 请求更多的历史数据
    });

    const url = `${API_CONFIG.BASE_URL}?${params.toString()}`;

    const response = await axios.get(url, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });

    if (!response.data || !response.data.Data) {
      throw new Error("Invalid API response format");
    }

    const data = response.data.Data as PriceDataItem[];

    if (!Array.isArray(data) || data.length === 0) {
      throw new Error("No price data available");
    }

    console.log("Raw API response:", data[0]); // 调试日志：查看原始数据格式

    // 验证并排序数据（确保按时间升序排列）
    const sortedData = [...data].sort((a, b) => a.TIMESTAMP - b.TIMESTAMP);

    // 转换价格数据为数组格式，使用收盘价
    const prices = sortedData.map((item: PriceDataItem) => {
      if (!item.TIMESTAMP || !item.CLOSE) {
        console.error("Invalid data item:", item);
        throw new Error("Missing required price data fields");
      }

      const timestamp = item.TIMESTAMP * 1000; // 转换为毫秒
      const price = parseFloat(String(item.CLOSE)); // 确保价格是数值类型
      const date = new Date(timestamp).toISOString().split("T")[0];

      return { timestamp, price, date };
    });

    if (prices.length < 2) {
      throw new Error("Insufficient price data for volatility calculation");
    }

    // 计算每日对数收益率
    const logReturns = [];
    for (let i = 1; i < prices.length; i++) {
      const previousPrice = prices[i - 1].price;
      const currentPrice = prices[i].price;

      if (previousPrice <= 0 || currentPrice <= 0) {
        console.error(
          `Invalid price values: prev=${previousPrice}, curr=${currentPrice}`
        );
        continue;
      }

      const logReturn = Math.log(currentPrice / previousPrice);

      logReturns.push({
        date: prices[i].date,
        value: logReturn,
        price: currentPrice,
      });
    }

    if (logReturns.length === 0) {
      throw new Error("No valid returns could be calculated");
    }

    // 使用30天的滚动窗口计算波动率
    const window = Math.min(30, logReturns.length); // 确保窗口大小不超过数据长度
    const volatilities = [];
    const annualizationFactor = Math.sqrt(365); // 年化因子

    for (let i = window - 1; i < logReturns.length; i++) {
      // 获取窗口的收益率数据
      const windowLogReturns = logReturns.slice(i - window + 1, i + 1);

      // 计算平均对数收益率
      const mean =
        windowLogReturns.reduce((sum, item) => sum + item.value, 0) / window;

      // 计算方差
      const variance =
        windowLogReturns.reduce((sum, item) => {
          const deviation = item.value - mean;
          return sum + deviation * deviation;
        }, 0) /
        (window - 1);

      // 计算标准差（波动率）
      const stdDev = Math.sqrt(variance);

      // 计算年化波动率（以百分比表示）
      const annualizedVol = stdDev * annualizationFactor * 100;

      volatilities.push({
        date: logReturns[i].date,
        value: parseFloat(annualizedVol.toFixed(2)),
        price: parseFloat(logReturns[i].price.toFixed(2)),
      });
    }

    // 在计算完波动率后，只保留用户请求的天数
    const trimmedData = volatilities.slice(-days);

    if (trimmedData.length === 0) {
      throw new Error("No volatility data available after processing");
    }

    // 添加调试日志
    console.log(`${coinKey} 数据处理完成:`);
    console.log(`- 请求天数: ${requiredDays} (显示 ${days} 天)`);
    console.log(`- 原始数据点数: ${data.length}`);
    console.log(`- 价格数据点数: ${prices.length}`);
    console.log(`- 收益率数据点数: ${logReturns.length}`);
    console.log(`- 最终数据点数: ${trimmedData.length}`);
    console.log(
      `- 时间范围: ${trimmedData[0].date} 至 ${
        trimmedData[trimmedData.length - 1].date
      }`
    );
    console.log(
      `- 波动率范围: ${Math.min(
        ...trimmedData.map((d) => d.value)
      )}% - ${Math.max(...trimmedData.map((d) => d.value))}%`
    );
    console.log(
      `- 价格范围: $${Math.min(
        ...trimmedData.map((d) => d.price)
      )} - $${Math.max(...trimmedData.map((d) => d.price))}`
    );

    volatilityData.value[coinKey] = trimmedData;
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

    // 添加自定义鼠标事件处理
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

          // 确保索引有效且与当前高亮点不同
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

            // 取消之前的高亮点
            if (currentHighlightIndex.value[coinKey] !== -1) {
              charts.value[coinKey]!.dispatchAction({
                type: "downplay",
                seriesIndex: [0, 1],
                dataIndex: currentHighlightIndex.value[coinKey],
              });
            }

            // 高亮当前点
            charts.value[coinKey]!.dispatchAction({
              type: "highlight",
              seriesIndex: [0, 1],
              dataIndex: xIndex,
            });

            // 更新当前高亮点索引
            currentHighlightIndex.value[coinKey] = xIndex;
          }
        } else {
          customTooltip.value[coinKey].show = false;

          // 取消高亮
          if (currentHighlightIndex.value[coinKey] !== -1) {
            charts.value[coinKey]!.dispatchAction({
              type: "downplay",
              seriesIndex: [0, 1],
              dataIndex: currentHighlightIndex.value[coinKey],
            });
            currentHighlightIndex.value[coinKey] = -1;
          }
        }
      } catch (e) {
        console.error(`Error in mousemove handler:`, e);
        customTooltip.value[coinKey].show = false;
      }
    }, 100);

    const handleMouseLeave = () => {
      customTooltip.value[coinKey].show = false;

      // 取消高亮
      if (currentHighlightIndex.value[coinKey] !== -1) {
        charts.value[coinKey]!.dispatchAction({
          type: "downplay",
          seriesIndex: [0, 1],
          dataIndex: currentHighlightIndex.value[coinKey],
        });
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
    }, 100);

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

  // fetch("http://localhost:3000/api/price-history?symbol=BTC&days=30").then(
  //   (response) => {
  //     console.log(response);
  //   }
  // );
});
</script>

<template>
  <div class="cmc-volatility">
    <div class="page-header">
      <h1>coindesk 历史波动率分析</h1>
    </div>

    <div class="time-selector">
      <el-radio-group v-model="timeWindow" @change="changeTimeWindow">
        <el-radio-button :label="30">30天</el-radio-button>
        <el-radio-button :label="60">60天</el-radio-button>
        <el-radio-button :label="90">90天</el-radio-button>
        <el-radio-button :label="180">180天</el-radio-button>
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
          <div v-if="solanaStats" class="volatility-metrics-card">
            <div class="metrics-header">SOL 历史波动率指标</div>
            <div class="metrics-grid">
              <div class="metric-item">
                <div class="metric-label">当前波动率</div>
                <div
                  class="metric-value"
                  :class="getVolatilityClass(solanaStats.current)"
                >
                  {{ solanaStats.current }}% ({{
                    getVolatilityStatus(solanaStats.current)
                  }})
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-label">平均波动率</div>
                <div class="metric-value">{{ solanaStats.avg }}%</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">最大波动率</div>
                <div class="metric-value text-danger">
                  {{ solanaStats.max }}% ({{ formatDate(solanaStats.maxDate) }})
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-label">最小波动率</div>
                <div class="metric-value text-success">
                  {{ solanaStats.min }}% ({{ formatDate(solanaStats.minDate) }})
                </div>
              </div>
            </div>
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
          <div v-if="bitcoinStats" class="volatility-metrics-card">
            <div class="metrics-header">BTC 历史波动率指标</div>
            <div class="metrics-grid">
              <div class="metric-item">
                <div class="metric-label">当前波动率</div>
                <div
                  class="metric-value"
                  :class="getVolatilityClass(bitcoinStats.current)"
                >
                  {{ bitcoinStats.current }}% ({{
                    getVolatilityStatus(bitcoinStats.current)
                  }})
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-label">平均波动率</div>
                <div class="metric-value">{{ bitcoinStats.avg }}%</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">最大波动率</div>
                <div class="metric-value text-danger">
                  {{ bitcoinStats.max }}% ({{
                    formatDate(bitcoinStats.maxDate)
                  }})
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-label">最小波动率</div>
                <div class="metric-value text-success">
                  {{ bitcoinStats.min }}% ({{
                    formatDate(bitcoinStats.minDate)
                  }})
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cmc-volatility {
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 20px;
}

.page-header h1 {
  color: #333;
  margin-bottom: 5px;
}

.api-info {
  color: #666;
  font-size: 14px;
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

.implementation-notes {
  margin-top: 40px;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.implementation-notes h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metric-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.metric-section h4 {
  color: #409eff;
  margin-bottom: 15px;
  font-size: 16px;
}

.metric-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.metric-section li {
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
  position: relative;
  padding-left: 20px;
}

.metric-section li::before {
  content: "•";
  color: #409eff;
  position: absolute;
  left: 0;
  font-weight: bold;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .metric-section {
    margin-bottom: 15px;
  }
}

.volatility-metrics-card {
  margin-top: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.metrics-header {
  background-color: #f5f7fa;
  padding: 12px 20px;
  font-weight: bold;
  color: #2c3e50;
  border-bottom: 1px solid #ebeef5;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background-color: #ebeef5;
}

.metric-item {
  background-color: white;
  padding: 15px 20px;
}

.metric-label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
}

.text-success {
  color: #67c23a !important;
}

.text-warning {
  color: #e6a23c !important;
}

.text-danger {
  color: #f56c6c !important;
}
</style>
