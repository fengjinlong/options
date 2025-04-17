<template>
  <div class="option-chart">
    <div class="input-section">
      <el-form :inline="true" class="option-form">
        <div class="option-group">
          <h3>短期卖出看涨期权</h3>
          <el-form-item label="行权价">
            <el-input-number
              v-model="shortStrike"
              :min="60"
              :max="140"
              :step="1"
              @change="updateChart"
            />
          </el-form-item>
          <el-form-item label="权利金">
            <el-input-number
              v-model="shortPremium"
              :min="0"
              :max="20"
              :step="0.5"
              @change="updateChart"
            />
          </el-form-item>
          <el-form-item label="到期价格">
            <el-input-number
              v-model="shortExpiryPrice"
              :min="60"
              :max="140"
              :step="1"
              @change="updateChart"
            />
          </el-form-item>
        </div>

        <div class="option-group">
          <h3>长期买入看涨期权</h3>
          <el-form-item label="行权价">
            <el-input-number
              v-model="longStrike"
              :min="60"
              :max="140"
              :step="1"
              @change="updateChart"
            />
          </el-form-item>
          <el-form-item label="权利金">
            <el-input-number
              v-model="longPremium"
              :min="0"
              :max="20"
              :step="0.5"
              @change="updateChart"
            />
          </el-form-item>
        </div>
      </el-form>
    </div>
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from "vue";
import * as echarts from "echarts";

const chartContainer = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

// 期权参数
const shortStrike = ref(100); // 短期期权行权价
const shortPremium = ref(5); // 短期期权权利金
const shortExpiryPrice = ref(100); // 短期期权到期价格
const longStrike = ref(100); // 长期期权行权价
const longPremium = ref(8); // 长期期权权利金

// 计算短期期权到期时的盈亏
const calculateShortOptionPL = (expiryPrice: number) => {
  // 如果到期价格高于行权价，买方会行权，卖方亏损
  // 如果到期价格低于等于行权价，买方不会行权，卖方获得全部权利金
  return expiryPrice > shortStrike.value
    ? -(expiryPrice - shortStrike.value) + shortPremium.value
    : shortPremium.value;
};

// 模拟数据生成函数
const generateData = (shortExpiryPrice: number) => {
  // 生成价格范围（比最小行权价低20，比最大行权价高20）
  const minPrice = Math.min(shortStrike.value, longStrike.value) - 20;
  const maxPrice = Math.max(shortStrike.value, longStrike.value) + 20;
  const priceCount = maxPrice - minPrice + 1;
  const prices = Array.from({ length: priceCount }, (_, i) => minPrice + i);

  // 计算短期期权到期时的盈亏（固定值）
  const shortPL = calculateShortOptionPL(shortExpiryPrice);

  // 生成长期期权在不同价格下的盈亏
  const longExpiryPL = prices.map((price) => {
    // 长期看涨期权最终收益
    const longValue = Math.max(0, price - longStrike.value);
    // 总盈亏 = 短期期权盈亏（固定） + 长期期权盈亏
    return shortPL + longValue - longPremium.value;
  });

  return {
    xAxis: prices,
    series: [longExpiryPL],
    shortPL,
  };
};

// 初始化图表配置
const initChart = () => {
  if (!chartContainer.value) return;
  chart = echarts.init(chartContainer.value);
  updateChart();
};

// 更新图表
const updateChart = () => {
  if (!chart) return;

  const {
    xAxis: prices,
    series,
    shortPL,
  } = generateData(shortExpiryPrice.value);

  const option: echarts.EChartsOption = {
    title: {
      text: `日历差价看涨组合盈亏曲线 (短期期权盈亏: ${shortPL.toFixed(2)})`,
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        if (!Array.isArray(params)) return "";
        const price = params[0].axisValue;
        return `标的价格: ${price}
短期期权盈亏: ${shortPL.toFixed(2)}
组合总盈亏: ${params[0].data.toFixed(2)}`;
      },
    },
    legend: {
      data: ["组合盈亏"],
      top: 30,
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: prices,
      name: "标的价格",
    },
    yAxis: {
      type: "value",
      name: "盈亏",
      axisLabel: {
        formatter: "{value}",
      },
    },
    series: [
      {
        name: "组合盈亏",
        type: "line",
        data: series[0],
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: "#35b115" },
      },
    ],
    markLine: {
      data: [
        {
          name: "短期行权价",
          xAxis: shortStrike.value,
          lineStyle: {
            type: "dashed",
          },
          label: {
            formatter: `短期行权价: ${shortStrike.value}`,
          },
        },
        {
          name: "长期行权价",
          xAxis: longStrike.value,
          lineStyle: {
            type: "dashed",
            color: "#91cc75",
          },
          label: {
            formatter: `长期行权价: ${longStrike.value}`,
          },
        },
        {
          name: "短期到期价",
          xAxis: shortExpiryPrice.value,
          lineStyle: {
            type: "dashed",
            color: "#ee6666",
          },
          label: {
            formatter: `到期价: ${shortExpiryPrice.value}`,
          },
        },
        {
          name: "盈亏平衡点",
          yAxis: 0,
          lineStyle: {
            type: "dashed",
          },
          label: {
            formatter: "盈亏平衡",
          },
        },
      ],
    },
  };

  chart.setOption(option);
};

// 监听窗口大小变化
const handleResize = () => {
  chart?.resize();
};

onMounted(() => {
  initChart();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  chart?.dispose();
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.option-chart {
  padding: 20px;
}

.input-section {
  margin-bottom: 20px;
}

.option-form {
  display: flex;
  gap: 40px;
}

.option-group {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.option-group h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #606266;
}

.chart-container {
  width: 100%;
  height: 600px;
}
</style>
