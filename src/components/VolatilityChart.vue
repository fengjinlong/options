<template>
  <div class="volatility-chart-container">
    <div class="chart-header">
      <div class="title-section">
        <h2>Cryptocurrency Historical Volatility</h2>
        <div class="time-selector">
          <el-radio-group v-model="timeWindow" @change="handleTimeWindowChange">
            <el-radio-button :label="30">30天</el-radio-button>
            <el-radio-button :label="60">60天</el-radio-button>
            <el-radio-button :label="90">90天</el-radio-button>
            <el-radio-button :label="180">180天</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <el-select
        v-model="selectedCurrencies"
        multiple
        placeholder="Select currencies"
        @change="loadData"
      >
        <el-option
          v-for="currency in availableCurrencies"
          :key="currency"
          :label="currency"
          :value="currency"
        />
      </el-select>
    </div>

    <div v-if="loading" class="loading-container">
      <el-loading :fullscreen="false" text="Loading volatility data..." />
    </div>

    <div v-else-if="error" class="error-container">
      <el-alert :title="error" type="error" show-icon />
    </div>

    <div ref="chartRef" class="chart-container"></div>

    <div class="metrics-grid">
      <div
        v-for="currency in selectedCurrencies"
        :key="currency"
        class="metrics-card"
      >
        <div
          class="metrics-header"
          :style="{ borderColor: currencyColors[currency as keyof typeof currencyColors] }"
        >
          {{ currency }} 历史波动率指标
        </div>
        <div class="metrics-content" v-if="volatilityStats[currency]">
          <div class="metric-row">
            <div class="metric-item">
              <div class="metric-label">当前波动率</div>
              <div
                class="metric-value"
                :class="getVolatilityClass(volatilityStats[currency].current)"
              >
                {{ volatilityStats[currency].current }}% ({{
                  getVolatilityStatus(volatilityStats[currency].current)
                }})
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">平均波动率</div>
              <div class="metric-value">
                {{ volatilityStats[currency].avg }}%
              </div>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-item">
              <div class="metric-label">最大波动率</div>
              <div class="metric-value text-danger">
                {{ volatilityStats[currency].max }}%
                <span class="date-info"
                  >({{ formatDate(volatilityStats[currency].maxDate) }})</span
                >
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">最小波动率</div>
              <div class="metric-value text-success">
                {{ volatilityStats[currency].min }}%
                <span class="date-info"
                  >({{ formatDate(volatilityStats[currency].minDate) }})</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import * as echarts from "echarts";
import {
  ElLoading,
  ElSelect,
  ElOption,
  ElAlert,
  ElRadioGroup,
  ElRadioButton,
} from "element-plus";
import {
  fetchHistoricalVolatility,
  type VolatilityData,
} from "../services/deribit";

const chartRef = ref<HTMLElement | null>(null);
const chart = ref<echarts.ECharts | null>(null);
const loading = ref(false);
const error = ref("");
const timeWindow = ref(30); // 默认30天

const availableCurrencies = ["BTC", "SOL", "ETH"];
const selectedCurrencies = ref(["BTC", "SOL", "ETH"]);

const currencyColors = {
  BTC: "#F7931A",
  SOL: "#00FFA3",
  ETH: "#627EEA",
};

interface VolatilityStats {
  current: number;
  avg: number;
  max: number;
  maxDate: string;
  min: number;
  minDate: string;
}

const volatilityStats = ref<Record<string, VolatilityStats>>({});

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("zh-CN");
};

const getVolatilityStatus = (value: number) => {
  if (value < 50) return "低波动率";
  if (value < 100) return "中等波动率";
  if (value < 150) return "高波动率";
  return "极高波动率";
};

const getVolatilityClass = (value: number) => {
  if (value < 50) return "text-success";
  if (value < 100) return "text-warning";
  if (value < 150) return "text-danger";
  return "text-danger bold";
};

const calculateStats = (data: VolatilityData[]) => {
  if (!data.length) return null;

  const values = data.map((item) => item.value);
  const max = Math.max(...values);
  const maxIndex = values.indexOf(max);
  const min = Math.min(...values);
  const minIndex = values.indexOf(min);

  return {
    current: values[values.length - 1],
    avg: Number((values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)),
    max,
    maxDate: data[maxIndex].timestamp,
    min,
    minDate: data[minIndex].timestamp,
  };
};

const initChart = () => {
  if (!chartRef.value) return;

  chart.value = echarts.init(chartRef.value);
  const option: echarts.EChartsOption = {
    title: {
      text: "Historical Volatility Comparison",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
        animation: false,
        label: {
          backgroundColor: "#505765",
        },
      },
      formatter: (params: any) => {
        let result = `${new Date(
          params[0].axisValue
        ).toLocaleDateString()}<br/>`;
        params.forEach((param: any) => {
          const color =
            currencyColors[param.seriesName as keyof typeof currencyColors];
          result += `
            <span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${color};"></span>
            ${param.seriesName}: ${Number(param.value[1]).toFixed(2)}%<br/>
          `;
        });
        return result;
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "10%",
      top: "10%",
      containLabel: true,
    },
    xAxis: {
      type: "time",
      boundaryGap: ["3%", "3%"],
      axisLine: { lineStyle: { color: "#E0E6F1" } },
      axisLabel: {
        color: "#5E6573",
        formatter: (value: number) => {
          return new Date(value).toLocaleDateString();
        },
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: ["#E0E6F1"],
          type: "dashed",
        },
      },
    },
    yAxis: {
      type: "value",
      name: "Volatility (%)",
      nameTextStyle: {
        color: "#5E6573",
      },
      axisLine: { lineStyle: { color: "#E0E6F1" } },
      axisLabel: {
        color: "#5E6573",
        formatter: "{value}%",
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: ["#E0E6F1"],
          type: "dashed",
        },
      },
      min: 0,
      max: (value: { max: number }) => {
        // 向上取整到最近的 50
        return Math.ceil(value.max / 50) * 50;
      },
      interval: 50,
    },
    series: [],
  };

  chart.value.setOption(option);
  window.addEventListener("resize", () => chart.value?.resize());
};

const updateChartData = (data: Record<string, VolatilityData[]>) => {
  if (!chart.value) return;

  // Debug log
  Object.entries(data).forEach(([currency, values]) => {
    console.log(`${currency} data range:`, {
      min: Math.min(...values.map((v) => v.value)),
      max: Math.max(...values.map((v) => v.value)),
      first: values[0],
      last: values[values.length - 1],
    });
  });

  // Calculate stats for each currency
  Object.entries(data).forEach(([currency, values]) => {
    volatilityStats.value[currency] = calculateStats(values)!;
  });

  const series = Object.entries(data).map(([currency, values]) => ({
    name: currency,
    type: "line",
    smooth: true,
    symbol: "circle",
    symbolSize: 6,
    showSymbol: false,
    emphasis: {
      scale: true,
      focus: "series",
      itemStyle: {
        borderWidth: 2,
        shadowBlur: 10,
        shadowColor: "rgba(0, 0, 0, 0.3)",
      },
    },
    itemStyle: {
      color: currencyColors[currency as keyof typeof currencyColors],
      borderWidth: 2,
    },
    endLabel: {
      show: true,
      formatter: "{a}",
      color: currencyColors[currency as keyof typeof currencyColors],
    },
    data: values.map((item) => {
      // Debug log for any suspicious values
      if (item.value < 0.1 || item.value > 100) {
        console.log(`Suspicious value for ${currency}:`, item);
      }
      return [item.timestamp, item.value];
    }),
  }));

  chart.value.setOption({
    legend: {
      data: Object.keys(data),
      bottom: 0,
      textStyle: {
        color: "#5E6573",
      },
      itemStyle: {
        borderWidth: 2,
      },
    },
    series,
  });
};

const handleTimeWindowChange = () => {
  loadData();
};

const loadData = async () => {
  if (selectedCurrencies.value.length === 0) return;

  loading.value = true;
  error.value = "";

  try {
    const promises = selectedCurrencies.value.map((currency) =>
      fetchHistoricalVolatility(currency, `${timeWindow.value}D`)
    );

    const results = await Promise.all(promises);
    const data = selectedCurrencies.value.reduce((acc, currency, index) => {
      acc[currency] = results[index];
      return acc;
    }, {} as Record<string, VolatilityData[]>);

    // Debug log
    console.log("Processed data:", data);

    updateChartData(data);
  } catch (e) {
    error.value = "Failed to fetch volatility data. Please try again later.";
    console.error("Error loading volatility data:", e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  initChart();
  loadData();
});

watch(selectedCurrencies, () => {
  loadData();
});
</script>

<style scoped>
.volatility-chart-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.title-section h2 {
  margin: 0;
  color: #333;
}

.time-selector {
  margin-top: 10px;
}

.chart-container {
  height: 600px;
  width: 100%;
}

.loading-container {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-container {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

:deep(.el-radio-button__inner) {
  padding: 8px 15px;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-left: 1px solid #dcdfe6;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metrics-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.metrics-header {
  padding: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  background: #f8f9fa;
  border-bottom: 3px solid;
}

.metrics-content {
  padding: 20px;
}

.metric-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.metric-row:last-child {
  margin-bottom: 0;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-label {
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.date-info {
  font-size: 12px;
  color: #666;
  font-weight: normal;
  margin-left: 4px;
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

.text-danger.bold {
  font-weight: 700;
}
</style>
