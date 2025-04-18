<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from "vue";
import {
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElCard,
} from "element-plus";
import * as echarts from "echarts";
import type { EChartsOption, LegendComponentOption } from "echarts";

// 策略类型定义
const strategyTypes = [
  { label: "买入标的", value: "buyUnderlying" },
  { label: "买入看涨期权", value: "buyCall" },
  { label: "买入看跌期权", value: "buyPut" },
  { label: "卖出看涨期权", value: "sellCall" },
  { label: "卖出看跌期权", value: "sellPut" },
];

interface Strategy {
  id: number;
  type: string;
  strikePrice: number;
  premium: number;
}

// 表单数据
const strategies = ref<Strategy[]>([
  {
    id: 1,
    type: "buyCall",
    strikePrice: 100,
    premium: 5,
  },
]);

let nextId = 2;

// 图表实例
let chart: echarts.ECharts | null = null;

// 添加新策略
const addStrategy = () => {
  strategies.value.push({
    id: nextId++,
    type: "buyCall",
    strikePrice: 100,
    premium: 5,
  });
};

// 删除策略
const removeStrategy = (id: number) => {
  const index = strategies.value.findIndex((s) => s.id === id);
  if (index !== -1) {
    strategies.value.splice(index, 1);
  }
};

// 计算单个策略的盈亏
const calculateSingleStrategyProfitLoss = (
  strategy: Strategy,
  spotPrice: number
): number => {
  const { type, strikePrice, premium } = strategy;
  const K = strikePrice;
  const P = premium;
  const S = spotPrice;

  switch (type) {
    case "buyUnderlying":
      return S - K; // 买入标的的盈亏：现价 - 买入价
    case "buyCall":
      return S > K ? S - K - P : -P;
    case "buyPut":
      return S < K ? K - S - P : -P;
    case "sellCall":
      return S > K ? -(S - K) + P : P;
    case "sellPut":
      return S < K ? -(K - S) + P : P;
    default:
      return 0;
  }
};

// 计算组合策略的总盈亏
const calculateTotalProfitLoss = (spotPrice: number): number => {
  return strategies.value.reduce(
    (total, strategy) =>
      total + calculateSingleStrategyProfitLoss(strategy, spotPrice),
    0
  );
};

// 更新图表
const updateChart = () => {
  if (!chart) return;

  // 验证所有策略的行权价格是否有效
  const hasInvalidPrice = strategies.value.some((s) => {
    return (
      typeof s.strikePrice !== "number" ||
      isNaN(s.strikePrice) ||
      s.strikePrice <= 0
    );
  });

  if (hasInvalidPrice) {
    return; // 如果有无效价格，不更新图表
  }

  // 找出所有行权价的平均值作为基准价格
  const avgStrikePrice =
    strategies.value.reduce((sum, s) => sum + (s.strikePrice || 0), 0) /
    strategies.value.length;

  if (!avgStrikePrice || isNaN(avgStrikePrice)) {
    return; // 如果平均价格无效，不更新图表
  }

  const xData: number[] = [];
  const yData: number[] = [];
  const individualStrategyData: number[][] = strategies.value.map(() => []);

  // 生成数据点
  const minPrice = avgStrikePrice * 0.5;
  const maxPrice = avgStrikePrice * 1.5;
  const step = avgStrikePrice * 0.01;

  for (let price = minPrice; price <= maxPrice; price += step) {
    xData.push(price);
    yData.push(calculateTotalProfitLoss(price));

    // 计算每个单独策略的盈亏
    strategies.value.forEach((strategy, index) => {
      individualStrategyData[index].push(
        calculateSingleStrategyProfitLoss(strategy, price)
      );
    });
  }

  // 查找平衡点（盈亏为0的点）
  const breakEvenPoints: number[] = [];
  for (let i = 1; i < yData.length; i++) {
    if (
      (yData[i - 1] <= 0 && yData[i] >= 0) ||
      (yData[i - 1] >= 0 && yData[i] <= 0)
    ) {
      // 使用线性插值找到更精确的平衡点
      const x1 = xData[i - 1];
      const x2 = xData[i];
      const y1 = yData[i - 1];
      const y2 = yData[i];
      const breakEvenPrice = x1 + ((x2 - x1) * (0 - y1)) / (y2 - y1);
      breakEvenPoints.push(breakEvenPrice);
    }
  }

  // 找出最大盈利和最大亏损
  const maxProfit = Math.max(...yData);
  const maxLoss = Math.min(...yData);

  const option: EChartsOption = {
    title: {
      text: "盈亏图",
      left: "center",
    },
    color: ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399"],
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        const price = params[0].data[0];
        let result = `标的价格: ${price.toFixed(2)}<br/>`;
        params.forEach((param: any) => {
          if (param.seriesName === "总盈亏") {
            result += `总盈亏: ${param.data[1].toFixed(2)}<br/>`;
          } else {
            const strategyIndex = strategies.value.findIndex(
              (s) => `策略${s.id}` === param.seriesName
            );
            if (strategyIndex !== -1) {
              result += `${param.seriesName}: ${param.data[1].toFixed(2)}<br/>`;
            }
          }
        });
        return result;
      },
    },
    legend: {
      data: ["总盈亏", ...strategies.value.map((s) => `策略${s.id}`)],
      top: 30,
      selected: {
        总盈亏: true,
        ...Object.fromEntries(
          strategies.value.map((s) => [`策略${s.id}`, true])
        ),
      },
    },
    xAxis: {
      type: "value",
      name: "标的价格",
      nameLocation: "middle",
      nameGap: 30,
    },
    yAxis: {
      type: "value",
      name: "盈亏",
      nameLocation: "middle",
      nameGap: 40,
    },
    series: [
      {
        name: "总盈亏",
        type: "line",
        data: xData.map((x, index) => [x, yData[index]]),
        smooth: true,
        lineStyle: { width: 1 },
        markLine: {
          symbol: ["none", "none"],
          silent: true,
          data: [
            { yAxis: 0 },
            ...(maxProfit > 0
              ? [
                  {
                    yAxis: maxProfit,
                    name: `最大盈利: ${maxProfit.toFixed(2)}`,
                  },
                ]
              : []),
            ...(maxLoss < 0
              ? [{ yAxis: maxLoss, name: `最大亏损: ${maxLoss.toFixed(2)}` }]
              : []),
          ],
          label: {
            formatter: "{b}",
            position: "insideEndTop",
          },
        },
        markPoint: {
          silent: true,
          data: [
            ...breakEvenPoints.map((price) => ({
              coord: [price, 0],
              name: `${price.toFixed(2)}`,
              symbol: "circle",
              symbolSize: 8,
              label: {
                show: true,
                formatter: "{b}",
                position: "inside" as const,
                color: "#67C23A",
                backgroundColor: "rgba(255, 255, 255, 0.9)",
                padding: [4, 8],
                borderRadius: 4,
              },
              itemStyle: {
                color: "#67C23A",
              },
            })),
          ],
          label: {
            formatter: "{b}\n{c}",
            position: "inside",
          },
        },
      },
      ...individualStrategyData.map((data, index) => ({
        name: `策略${strategies.value[index].id}`,
        type: "line" as const,
        data: xData.map((x, i) => [x, data[i]]),
        smooth: true,
        lineStyle: { width: 1, opacity: 0.6 },
      })),
    ],
  };

  // 设置图表选项
  chart.setOption(option, true);

  // 添加图例事件监听
  chart.off("legendselectchanged");
  chart.on("legendselectchanged", () => {
    if (!chart) return;

    // 获取当前图例选中状态
    const currentOption = chart.getOption();
    if (
      !currentOption ||
      !currentOption.legend ||
      !Array.isArray(currentOption.legend)
    )
      return;

    const legendSelected = currentOption.legend[0].selected;
    if (!legendSelected) return;

    const selected = legendSelected as Record<string, boolean>;

    // 检查是否所有策略都被隐藏
    const hasVisibleStrategy = Object.entries(selected).some(
      ([key, value]) => key !== "总盈亏" && value === true
    );

    // 如果所有策略都被隐藏，也隐藏总盈亏
    if (!hasVisibleStrategy && selected["总盈亏"]) {
      chart.dispatchAction({
        type: "legendToggleSelect",
        name: "总盈亏",
      });
    }
  });
};

// 监听策略变化
watch(
  strategies,
  () => {
    updateChart();
  },
  { deep: true }
);

// 初始化图表
onMounted(() => {
  const chartDom = document.getElementById("profitLossChart");
  if (chartDom) {
    chart = echarts.init(chartDom);
    updateChart();

    // 添加窗口大小变化时的图表重绘
    window.addEventListener("resize", () => {
      chart?.resize();
    });
  }
});

// 添加 onUnmounted 清理事件监听
onUnmounted(() => {
  window.removeEventListener("resize", () => {
    chart?.resize();
  });
  chart?.dispose();
});
</script>

<template>
  <div class="options-calculator">
    <!-- <h2>计算器</h2> -->

    <div class="main-container">
      <el-button type="primary" @click="addStrategy">添加策略</el-button>
      <div class="strategies-container">
        <el-card
          v-for="(strategy, index) in strategies"
          :key="strategy.id"
          class="strategy-card"
        >
          <template #header>
            <div class="card-header">
              <!-- <span>策略 {{ strategy.id }}</span> -->
              <span>策略 {{ index + 1 }}</span>
              <el-button
                type="danger"
                link
                size="small"
                @click="removeStrategy(strategy.id)"
                :disabled="strategies.length === 1"
              >
                删除
              </el-button>
            </div>
          </template>

          <el-form label-width="100px">
            <el-form-item label="策略类型">
              <el-select v-model="strategy.type">
                <el-option
                  v-for="item in strategyTypes"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item
              :label="
                strategy.type === 'buyUnderlying' ? '买入价格' : '行权价格'
              "
            >
              <el-input
                v-model.number="strategy.strikePrice"
                type="number"
                :min="0"
                @blur="(e) => {
                  const target = e.target as HTMLInputElement;
                  const numVal = Number(target.value);
                  if (!numVal || numVal <= 0) {
                    strategy.strikePrice = 100; // 设置默认值
                  }
                }"
                :placeholder="
                  strategy.type === 'buyUnderlying'
                    ? '请输入买入价格'
                    : '请输入行权价格'
                "
              />
            </el-form-item>

            <el-form-item
              label="期权费"
              v-if="strategy.type !== 'buyUnderlying'"
            >
              <el-input
                v-model.number="strategy.premium"
                type="number"
                placeholder="请输入期权费"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- <div class="add-strategy">
          <el-button type="primary" @click="addStrategy">添加策略</el-button>
        </div> -->
      </div>

      <div class="chart-container">
        <div id="profitLossChart"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.options-calculator {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.main-container {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
  height: calc(100% - 60px); /* 减去标题的高度和边距 */
}

.strategies-container {
  width: 280px;
  flex-direction: column;
  gap: 20px;
  overflow-y: scroll;
  padding-right: 10px;
}

.strategy-card {
  width: 100%;
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.add-strategy {
  text-align: center;
  margin-top: auto;
  padding: 10px 0;
}

.chart-container {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  height: 100%;
  position: relative;
}

#profitLossChart {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

h2 {
  text-align: center;
  color: #409eff;
  margin-bottom: 20px;
  height: 40px;
}

/* 自定义滚动条样式 */
.strategies-container::-webkit-scrollbar {
  width: 6px;
}

.strategies-container::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.strategies-container::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}
</style>
