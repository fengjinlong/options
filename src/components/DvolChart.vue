<template>
  <div class="dvol-chart-container">
    <div v-if="loading" class="loading">Loading DVOL data...</div>
    <div v-else-if="error" class="error">
      {{ error }}
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

const initChart = () => {
  if (!chartRef.value) return;
  chart.value = echarts.init(chartRef.value);
};

const fetchData = async () => {
  try {
    const [btcData, ethData] = await Promise.all([
      getFullYearDvol("BTC"),
      getFullYearDvol("ETH"),
    ]);

    const option = {
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
          return params
            .map((item: any) => {
              return `${item.seriesName}: ${item.data[1].toFixed(
                2
              )}%<br/>Date: ${item.data[0]}`;
            })
            .join("<br/>");
        },
      },
      legend: {
        data: ["BTC DVOL", "ETH DVOL"],
        bottom: 10,
        selectedMode: true,
        selected: {
          "BTC DVOL": true,
          "ETH DVOL": true,
        },
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
          return Math.ceil(value.max / 10) * 10; // Round to nearest 10
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
          data: btcData.map((item) => [item.date, item.dvol]),
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
          data: ethData.map((item) => [item.date, item.dvol]),
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

    chart.value?.setOption(option);
    loading.value = false;
  } catch (e) {
    error.value = "Failed to fetch DVOL data. Please try again later.";
    loading.value = false;
    console.error("Error fetching DVOL data:", e);
  }
};

const handleResize = () => {
  chart.value?.resize();
};

onMounted(() => {
  initChart();
  fetchData();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  chart.value?.dispose();
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
</style>
