<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue";
import axios from "axios";
import * as echarts from "echarts";

// 状态变量
const loading = ref(true);
const error = ref<string | null>(null);
const chart = ref<echarts.ECharts | null>(null);
const chartContainer = ref<HTMLElement | null>(null);
const timeWindow = ref(30); // 默认30天
const volatilityData = ref<{ date: string; value: number }[]>([]);
const selectedCoin = ref<"solana" | "bitcoin">("solana"); // 默认选择SOL

// 获取加密货币的名称
const coinDisplayName = computed(() => {
  return selectedCoin.value === "solana" ? "SOL" : "BTC";
});

// 获取历史价格数据
const fetchPriceData = async (coin: string, days: number) => {
  loading.value = true;
  error.value = null;

  try {
    // 使用CoinGecko API获取历史价格
    const response = await axios.get(
      `https://api.coingecko.com/api/v3/coins/${coin}/market_chart`,
      {
        params: {
          vs_currency: "usd",
          days: days,
          interval: "daily",
        },
      }
    );

    // 提取价格数据
    const prices = response.data.prices;
    console.log(`Received ${coin} price data:`, prices.length, "data points");

    // 计算对数收益率
    const logReturns = [];
    for (let i = 1; i < prices.length; i++) {
      const previousPrice = prices[i - 1][1];
      const currentPrice = prices[i][1];
      logReturns.push(Math.log(currentPrice / previousPrice));
    }

    // 计算N天滚动波动率，使用20天窗口
    const window = Math.min(30, logReturns.length);
    const volatilities = [];

    for (let i = window - 1; i < logReturns.length; i++) {
      const windowLogReturns = logReturns.slice(i - window + 1, i + 1);

      // 计算标准差
      const mean =
        windowLogReturns.reduce((a, b) => a + b, 0) / windowLogReturns.length;
      const variance =
        windowLogReturns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) /
        windowLogReturns.length;
      const stdDev = Math.sqrt(variance);

      // 计算年化波动率 (标准差 * sqrt(252))
      const annualizedVol = stdDev * Math.sqrt(365) * 100; // 转为百分比

      // 使用对应日期
      const date = new Date(prices[i + 1][0]);
      const dateStr = date.toISOString().split("T")[0];

      volatilities.push({
        date: dateStr,
        value: parseFloat(annualizedVol.toFixed(2)),
      });
    }

    volatilityData.value = volatilities;
    console.log(
      "Calculated volatility data:",
      volatilityData.value.length,
      "points"
    );

    // 设置loading为false以显示图表容器
    loading.value = false;

    // 使用setTimeout确保DOM已经更新后再初始化图表
    setTimeout(() => {
      console.log("Timeout after data fetch, attempting to initialize chart");
      console.log("Chart container exists:", !!chartContainer.value);
      initChart();
    }, 100);
  } catch (err) {
    console.error(`Failed to fetch ${coin} price data:`, err);
    error.value = "获取数据失败，请稍后再试";
    loading.value = false;
  }
};

// 初始化ECharts图表
const initChart = () => {
  console.log("Initializing chart, container exists:", !!chartContainer.value);
  if (!chartContainer.value) {
    console.error("Chart container not found");
    // 延迟重试一次
    setTimeout(() => {
      console.log("Retrying chart initialization...");
      if (chartContainer.value) {
        doInitChart();
      } else {
        console.error("Chart container still not found after retry");
      }
    }, 100);
    return;
  }

  doInitChart();
};

// 实际执行图表初始化的函数
const doInitChart = () => {
  if (chart.value) {
    chart.value.dispose();
  }

  try {
    chart.value = echarts.init(chartContainer.value);
    console.log("Chart initialized successfully");

    const dates = volatilityData.value.map((item) => item.date);
    const values = volatilityData.value.map((item) => item.value);

    console.log("Chart data:", dates.length, "dates,", values.length, "values");

    // 计算均值和最大值
    const avgVol = parseFloat(
      (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
    );
    const maxVol = Math.max(...values);
    const maxVolDate = dates[values.indexOf(maxVol)];

    const option = {
      backgroundColor: "#ffffff",
      title: {
        text: `${coinDisplayName.value}历史波动率`,
        left: "center",
        textStyle: {
          fontSize: 18,
          fontWeight: "bold",
          color: "#333",
        },
        subtext: `${timeWindow.value}天数据分析`,
        subtextStyle: {
          color: "#999",
        },
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "cross",
          label: {
            backgroundColor: "#6a7985",
          },
        },
        formatter: function (params: any) {
          if (Array.isArray(params) && params.length > 0) {
            const date = params[0].axisValue;
            const value = params[0].data;
            return `<div style="font-size:14px;color:#666;font-weight:400;line-height:1;">
              <div>日期: ${date}</div>
              <div style="margin-top:5px;font-size:18px;color:#000;font-weight:bold;">
                波动率: ${value}%
              </div>
            </div>`;
          }
          return "";
        },
        backgroundColor: "rgba(255,255,255,0.9)",
        borderColor: "#ccc",
        borderWidth: 1,
        padding: [10, 15],
        textStyle: {
          color: "#333",
        },
        extraCssText: "box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);",
      },
      grid: {
        left: "5%",
        right: "5%",
        bottom: "12%",
        top: "15%",
        containLabel: true,
      },
      toolbox: {
        feature: {
          dataZoom: {
            yAxisIndex: "none",
          },
          saveAsImage: {
            pixelRatio: 2,
          },
          restore: {},
        },
        right: 20,
        top: 20,
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: dates,
        axisLine: {
          lineStyle: {
            color: "#999",
          },
        },
        axisLabel: {
          color: "#666",
          formatter: function (value: string) {
            // 简化日期显示: 2023-05-01 -> 05-01
            return value.substring(5);
          },
        },
        nameLocation: "middle",
        nameGap: 30,
      },
      yAxis: {
        type: "value",
        axisLabel: {
          formatter: "{value}%",
          color: "#666",
        },
        splitLine: {
          lineStyle: {
            color: ["#eee"],
          },
        },
        axisLine: {
          show: true,
          lineStyle: {
            color: "#999",
          },
        },
      },
      dataZoom: [
        {
          type: "inside",
          start: 0,
          end: 100,
          zoomLock: false,
        },
        {
          start: 0,
          end: 100,
          handleIcon:
            "path://M306.1,413c0,2.2-1.8,4-4,4h-59.8c-2.2,0-4-1.8-4-4v-2c0-2.2,1.8-4,4-4h59.8c2.2,0,4,1.8,4,4V413z",
          handleSize: "110%",
          handleStyle: {
            color: "#d3dee5",
          },
          textStyle: {
            color: "#999",
          },
          borderColor: "#90979c",
        },
      ],
      series: [
        {
          name: "年化波动率",
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          showSymbol: false,
          lineStyle: {
            width: 3,
            color: selectedCoin.value === "solana" ? "#5470c6" : "#F7931A",
          },
          emphasis: {
            focus: "series",
            itemStyle: {
              color: selectedCoin.value === "solana" ? "#5470c6" : "#F7931A",
              borderColor: "#fff",
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
          },
          data: values,
          markPoint: {
            data: [{ type: "max", name: "最大值" }],
          },
          markLine: {
            data: [{ type: "average", name: "平均值" }],
          },
        },
      ],
      visualMap: {
        show: false,
        dimension: 1,
        pieces: [
          {
            lte: 30,
            color: selectedCoin.value === "solana" ? "#3a73d2" : "#F7931A",
          },
          {
            gt: 30,
            lte: 50,
            color: selectedCoin.value === "solana" ? "#5470c6" : "#F7931A",
          },
          {
            gt: 50,
            lte: 70,
            color: selectedCoin.value === "solana" ? "#ec7a36" : "#e67e22",
          },
          {
            gt: 70,
            color: "#c23531",
          },
        ],
      },
    };

    chart.value.setOption(option);
    console.log("Chart option set successfully");
  } catch (err) {
    console.error("Error initializing chart:", err);
  }
};

// 监听窗口大小变化
window.addEventListener("resize", () => {
  if (chart.value) {
    chart.value.resize();
  }
});

// 更改时间窗口
const changeTimeWindow = (days: number) => {
  timeWindow.value = days;
  fetchPriceData(selectedCoin.value, days);
};

// 更改选择的加密货币
const changeCoin = (coin: "solana" | "bitcoin") => {
  selectedCoin.value = coin;
  fetchPriceData(selectedCoin.value, timeWindow.value);
};

// 统计信息
const statistics = computed(() => {
  if (!volatilityData.value.length) return null;

  const values = volatilityData.value.map((item) => item.value);
  const max = Math.max(...values);
  const maxDate = volatilityData.value[values.indexOf(max)].date;
  const min = Math.min(...values);
  const minDate = volatilityData.value[values.indexOf(min)].date;
  const avg = parseFloat(
    (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
  );
  const current = values[values.length - 1]; // 最新的波动率
  const startDate = volatilityData.value[0].date;
  const endDate = volatilityData.value[volatilityData.value.length - 1].date;

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
});

// 获取波动率状态描述
const getVolatilityStatus = () => {
  if (!statistics.value) return "";

  const current = statistics.value.current;

  if (current < 30) {
    return "低波动率";
  } else if (current < 50) {
    return "中等波动率";
  } else if (current < 70) {
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
  console.log("Component mounted");
  // 等待下一个tick，确保DOM已渲染
  await nextTick();
  console.log(
    "Next tick after mount, chartContainer exists:",
    !!chartContainer.value
  );
  fetchPriceData(selectedCoin.value, timeWindow.value);
});
</script>

<template>
  <div class="sol-volatility">
    <h2>{{ coinDisplayName }} 历史波动率分析</h2>

    <div class="selector-container">
      <div class="coin-selector">
        <el-radio-group v-model="selectedCoin" @change="changeCoin">
          <el-radio-button label="solana">
            <span class="coin-label">
              <span class="coin-icon solana"></span>SOL
            </span>
          </el-radio-button>
          <el-radio-button label="bitcoin">
            <span class="coin-label">
              <span class="coin-icon bitcoin"></span>BTC
            </span>
          </el-radio-button>
        </el-radio-group>
      </div>

      <div class="time-selector">
        <el-radio-group v-model="timeWindow" @change="changeTimeWindow">
          <el-radio-button :label="30">30天</el-radio-button>
          <el-radio-button :label="60">60天</el-radio-button>
          <el-radio-button :label="90">90天</el-radio-button>
          <el-radio-button :label="180">180天</el-radio-button>
          <el-radio-button :label="365">1年</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else-if="error" class="error-message">
      <el-alert :title="error" type="error" />
    </div>

    <div v-else class="chart-container">
      <div ref="chartContainer" class="chart-div"></div>

      <div v-if="statistics" class="statistics">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>{{ coinDisplayName }} 历史波动率指标</span>
                </div>
              </template>
              <el-descriptions border :column="1">
                <el-descriptions-item label="当前波动率">
                  <span :class="getVolatilityClass(statistics.current)"
                    >{{ statistics.current }}%</span
                  >
                </el-descriptions-item>
                <el-descriptions-item label="最大波动率">
                  <span class="text-danger"
                    >{{ statistics.max }}% ({{ statistics.maxDate }})</span
                  >
                </el-descriptions-item>
                <el-descriptions-item label="最小波动率">
                  <span class="text-success"
                    >{{ statistics.min }}% ({{ statistics.minDate }})</span
                  >
                </el-descriptions-item>
                <el-descriptions-item label="平均波动率">
                  {{ statistics.avg }}%
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>波动率分析</span>
                </div>
              </template>
              <div class="analysis">
                <p>
                  <strong>波动率状态:</strong>
                  <span :class="getVolatilityClass(statistics.current)">{{
                    getVolatilityStatus()
                  }}</span>
                </p>
                <p><strong>数据周期:</strong> {{ timeWindow }}天</p>
                <p><strong>数据点数:</strong> {{ volatilityData.length }}个</p>
                <p>
                  <strong>数据范围:</strong> {{ statistics.startDate }} 至
                  {{ statistics.endDate }}
                </p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sol-volatility {
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.selector-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.coin-selector {
  margin-bottom: 10px;
}

.coin-label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.coin-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-size: cover;
}

.solana {
  background-color: #9945ff;
}

.bitcoin {
  background-color: #f7931a;
}

.time-selector {
  display: flex;
  justify-content: center;
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
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-div {
  width: 100%;
  height: 500px;
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

.analysis {
  line-height: 1.8;
}
</style>
