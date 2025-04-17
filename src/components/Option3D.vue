<template>
  <div class="option-3d-container">
    <div ref="plotContainer" class="plot-container"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import Plotly from "plotly.js-dist-min";

const plotContainer = ref<HTMLElement | null>(null);

// 生成模拟数据
const generateData = () => {
  // X轴：价格区间（60-140，因为行权价相同，范围可以适当缩小）
  const priceRange = Array.from({ length: 81 }, (_, i) => 60 + i);

  // Y轴：到期日（短期和长期）
  const expiryDays = ["短期", "长期"];

  // 期权参数
  const strikePrice = 100; // 行权价
  const shortCallPremium = 5; // 短期期权费
  const longCallPremium = 8; // 长期期权费

  // Z轴：盈亏数据（二维数组，每行对应一个到期日）
  const profitLoss = expiryDays.map((period) => {
    return priceRange.map((price) => {
      let pl = 0;
      if (period === "短期") {
        // 短期卖出看涨期权
        pl =
          price > strikePrice
            ? -(price - strikePrice) + shortCallPremium
            : shortCallPremium;
      } else {
        // 长期买入看涨期权
        pl =
          price > strikePrice
            ? price - strikePrice - longCallPremium
            : -longCallPremium;
      }
      return pl;
    });
  });

  return {
    x: priceRange,
    y: expiryDays,
    z: profitLoss,
  };
};

// 初始化图表
const initPlot = () => {
  if (!plotContainer.value) return;

  const { x, y, z } = generateData();

  const data = [
    {
      type: "surface",
      x: x,
      y: y,
      z: z,
      colorscale: [
        [0, "#ff0000"], // 红色表示亏损
        [0.5, "#ffff00"], // 黄色表示盈亏平衡
        [1, "#00ff00"], // 绿色表示盈利
      ],
      contours: {
        z: {
          show: true,
          usecolormap: true,
          project: { z: true },
        },
      },
      hoverangular: true,
      hovertemplate:
        "价格: ¥%{x}<br>" +
        "期限: %{y}<br>" +
        "盈亏: ¥%{z:.2f}<br>" +
        "<extra></extra>",
    },
  ];

  const layout = {
    title: "日历差价组合（相同行权价）",
    autosize: true,
    scene: {
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.5 },
      },
      xaxis: {
        title: "标的价格",
        tickformat: ".0f",
        range: [60, 140],
        tickprefix: "¥",
      },
      yaxis: {
        title: "期限",
        tickformat: ".0f",
      },
      zaxis: {
        title: "盈亏",
        tickprefix: "¥",
      },
    },
    margin: {
      l: 65,
      r: 50,
      b: 65,
      t: 90,
    },
  };

  const config = {
    responsive: true,
    displayModeBar: true,
  };

  Plotly.newPlot(plotContainer.value, data, layout, config);
};

onMounted(() => {
  initPlot();
});
</script>

<style scoped>
.option-3d-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.plot-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
}
</style>
