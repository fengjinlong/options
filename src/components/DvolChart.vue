<template>
  <div class="dvol-chart-container">
    <div v-if="loading" class="loading">Loading DVOL data...</div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div class="stats-container" v-if="!loading && !error">
      <div class="stat-item">
        <h3>BTC IV Rank: {{ btcIVRank.toFixed(2) }}%</h3>
      </div>
      <div class="stat-item">
        <h3>ETH IV Rank: {{ ethIVRank.toFixed(2) }}%</h3>
      </div>
    </div>
    <div ref="chartRef" class="chart" style="width: 100%; height: 600px"></div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from "vue";
import * as echarts from "echarts";
import { getFullYearDvol } from "../services/deribit";

const chartRef = ref<HTMLElement | null>(null);
const chart = ref<echarts.ECharts | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const btcIVRank = ref(0);
const ethIVRank = ref(0);
const chartData = ref<{
  btcData: any[];
  ethData: any[];
}>({
  btcData: [],
  ethData: [],
});

// 计算百分位数的辅助函数
const getPercentile = (arr: number[], percentile: number) => {
  if (!arr || arr.length === 0) {
    console.warn("Empty array provided to getPercentile");
    return 0;
  }

  // 过滤掉无效值
  const validNumbers = arr.filter(
    (n) => typeof n === "number" && !isNaN(n) && n > 0
  );
  console.debug("Percentile calculation:", {
    originalLength: arr.length,
    validLength: validNumbers.length,
    percentile,
    sampleValues: validNumbers.slice(0, 5),
  });

  if (validNumbers.length === 0) {
    console.warn("No valid numbers for percentile calculation");
    return 0;
  }

  // 对数组进行排序
  const sorted = [...validNumbers].sort((a, b) => a - b);

  // 计算位置
  const position = (sorted.length - 1) * percentile;
  const base = Math.floor(position);
  const rest = position - base;

  const result =
    sorted[base + 1] !== undefined
      ? sorted[base] + rest * (sorted[base + 1] - sorted[base])
      : sorted[base];

  console.debug("Percentile result:", {
    percentile,
    result,
    min: sorted[0],
    max: sorted[sorted.length - 1],
  });

  return result;
};

// 计算中位数
const calculateMedian = (sortedArr: number[]): number => {
  const mid = Math.floor(sortedArr.length / 2);
  return sortedArr.length % 2 !== 0
    ? sortedArr[mid]
    : (sortedArr[mid - 1] + sortedArr[mid]) / 2;
};

// 计算四分位数
const calculateQuartiles = (sortedData: number[]) => {
  const n = sortedData.length;
  if (n === 0) return { q1: null, q3: null };

  const lowerHalf = sortedData.slice(0, Math.floor(n / 2));
  const upperHalf =
    n % 2 === 0
      ? sortedData.slice(Math.floor(n / 2))
      : sortedData.slice(Math.floor(n / 2) + 1);

  return {
    q1: calculateMedian(lowerHalf),
    q3: calculateMedian(upperHalf),
  };
};

// 计算 IV Rank，使用稳健的统计方法
const calculateIVRankWithLog = (currentIV: number, data: any[]) => {
  // 提取所有有效的 DVOL 值
  const dvolValues = data
    .map((item) => parseFloat(item.dvol))
    .filter((value) => !isNaN(value) && value > 0);

  if (dvolValues.length === 0) {
    console.warn("No valid DVOL values found");
    return 0;
  }

  const sortedData = [...dvolValues].sort((a, b) => a - b);
  const { q1, q3 } = calculateQuartiles(sortedData);

  if (q1 === null || q3 === null) {
    console.warn("Unable to calculate quartiles");
    return 0;
  }

  // 计算四分位距
  const iqr = q3 - q1;
  const kFactor = 1.5; // 可以根据需要调整

  // 计算初始的边界
  let lowerBound = q1 - kFactor * iqr;
  let upperBound = q3 + kFactor * iqr;

  // 检测异常值比例并动态调整 kFactor
  const outliers = dvolValues.filter((x) => x < lowerBound || x > upperBound);
  const outlierRatio = outliers.length / dvolValues.length;

  // 如果异常值太多，调整 kFactor
  let adjustedKFactor = kFactor;
  if (outlierRatio > 0.1) {
    adjustedKFactor = Math.max(1.0, kFactor * (1 - outlierRatio));
    lowerBound = q1 - adjustedKFactor * iqr;
    upperBound = q3 + adjustedKFactor * iqr;
  }

  // 使用百分位数进行 Winsorizing
  const p5Index = Math.floor(sortedData.length * 0.05);
  const p95Index = Math.floor(sortedData.length * 0.95);
  const p5 = sortedData[p5Index];
  const p95 = sortedData[p95Index];

  // Winsorizing 处理后的数据
  const winsorizedData = dvolValues.map((x) => {
    if (x < lowerBound) return p5;
    if (x > upperBound) return p95;
    return x;
  });

  const newMin = Math.min(...winsorizedData);
  const newMax = Math.max(...winsorizedData);

  console.debug("Statistical measures:", {
    q1,
    q3,
    iqr,
    originalBounds: { lower: lowerBound, upper: upperBound },
    outlierRatio,
    adjustedBounds: { lower: newMin, upper: newMax },
    currentValue: currentIV,
  });

  if (newMin === newMax) {
    console.warn("After winsorizing, min equals max");
    return currentIV === newMin ? 100 : 0;
  }

  // 计算最终的 rank
  let rank = ((currentIV - newMin) / (newMax - newMin)) * 100;

  // 确保结果在 0-100 之间
  rank = Math.min(Math.max(rank, 0), 100);

  console.debug("Final rank calculation:", {
    currentIV,
    newMin,
    newMax,
    rank,
  });

  return rank;
};

const getChartOption = () => {
  return {
    title: {
      text: "Deribit Volatility Index (DVOL 365)",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
      formatter: function (params: any) {
        if (!Array.isArray(params)) return "";
        return params
          .map((item: any) => {
            if (!item || !item.data) return "";
            const ivRank = item.seriesName.includes("BTC")
              ? calculateIVRankWithLog(item.data[1], chartData.value.btcData)
              : calculateIVRankWithLog(item.data[1], chartData.value.ethData);
            const data = item.seriesName.includes("BTC")
              ? chartData.value.btcData
              : chartData.value.ethData;
            const dvolValues = data.map((d) => d.dvol);
            const p5 = getPercentile(dvolValues, 0.2).toFixed(2);
            const p95 = getPercentile(dvolValues, 0.8).toFixed(2);

            return `${item.seriesName}: ${item.data[1].toFixed(2)}%<br/>
                   IV Rank (5%-95%): ${ivRank.toFixed(2)}%<br/>
                   5th Percentile: ${p5}%<br/>
                   95th Percentile: ${p95}%<br/>
                   Date: ${item.data[0]}`;
          })
          .filter(Boolean)
          .join("<br/>");
      },
    },
    legend: {
      data: ["BTC DVOL", "ETH DVOL"],
      bottom: 10,
      selectedMode: true,
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "time",
      boundaryGap: false,
      axisLabel: {
        rotate: 45,
        formatter: (value: string) => {
          return new Date(value).toLocaleDateString();
        },
      },
    },
    yAxis: {
      type: "value",
      name: "DVOL",
      min: 0,
      max: function (value: { max: number }) {
        return Math.ceil(value.max / 10) * 10;
      },
      splitLine: {
        show: true,
      },
      axisLabel: {
        formatter: "{value}",
      },
    },
    series: [
      {
        name: "BTC DVOL",
        type: "line",
        data: chartData.value.btcData.map((item) => [item.date, item.dvol]),
        smooth: true,
        showSymbol: false,
        lineStyle: {
          width: 2,
        },
        itemStyle: {
          color: "#67C23A",
        },
      },
      {
        name: "ETH DVOL",
        type: "line",
        data: chartData.value.ethData.map((item) => [item.date, item.dvol]),
        smooth: true,
        showSymbol: false,
        lineStyle: {
          width: 2,
        },
        itemStyle: {
          color: "#409EFF",
        },
      },
    ],
  };
};

const updateChart = () => {
  if (!chart.value) return;
  const option = getChartOption();
  try {
    chart.value.setOption(option, true);
  } catch (e) {
    console.error("Error updating chart:", e);
    // 如果更新失败，尝试重新初始化图表
    initChart();
  }
};

const initChart = () => {
  if (!chartRef.value) return;

  if (chart.value) {
    try {
      chart.value.dispose();
    } catch (e) {
      console.error("Error disposing chart:", e);
    }
  }

  try {
    chart.value = echarts.init(chartRef.value);
    updateChart();
  } catch (e) {
    console.error("Error initializing chart:", e);
    error.value = "Failed to initialize chart. Please refresh the page.";
  }
};

const fetchData = async () => {
  try {
    console.debug("Fetching DVOL data...");
    const [btcData, ethData] = await Promise.all([
      getFullYearDvol("BTC"),
      getFullYearDvol("ETH"),
    ]);

    // 验证数据
    if (!btcData?.length || !ethData?.length) {
      throw new Error("Invalid data received from API");
    }

    chartData.value = { btcData, ethData };

    // 获取最新的有效数据点
    const getLatestValidDvol = (data: any[]) => {
      const validData = data
        .slice()
        .reverse()
        .find((item) => {
          const dvol = parseFloat(item.dvol);
          return !isNaN(dvol) && dvol > 0;
        });

      return validData ? parseFloat(validData.dvol) : 0;
    };

    const currentBtcDvol = getLatestValidDvol(btcData);
    const currentEthDvol = getLatestValidDvol(ethData);

    console.debug("Latest values:", {
      btc: currentBtcDvol,
      eth: currentEthDvol,
    });

    btcIVRank.value = calculateIVRankWithLog(currentBtcDvol, btcData);
    ethIVRank.value = calculateIVRankWithLog(currentEthDvol, ethData);

    updateChart();
    loading.value = false;
  } catch (e) {
    error.value = "Failed to fetch DVOL data. Please try again later.";
    loading.value = false;
    console.error("Error fetching DVOL data:", e);
  }
};

const handleResize = () => {
  if (chart.value) {
    try {
      chart.value.resize();
    } catch (e) {
      console.error("Error resizing chart:", e);
    }
  }
};

onMounted(() => {
  initChart();
  fetchData();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  if (chart.value) {
    try {
      chart.value.dispose();
    } catch (e) {
      console.error("Error disposing chart:", e);
    }
  }
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.dvol-chart-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading,
.error {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.chart {
  margin-top: 20px;
}

.stats-container {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px 25px;
  background: #f5f7fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-item h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.stat-item:nth-child(1) h3 {
  color: #67c23a;
}

.stat-item:nth-child(2) h3 {
  color: #409eff;
}
</style>
