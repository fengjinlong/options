# 美股 PE 估值分析页面 — UsPeValuation

## 概述

`UsPeValuation.vue` 是一个用于分析美股 PE 估值水平的可视化页面，通过 FMP API 获取历史价格数据，结合本地 EPS 数据计算每日滚动 PE（TTM），并以多时间维度面板和 ECharts 图表的形式呈现估值分位。

---

## 核心功能

### 1. 股票选择器

页面顶部提供股票代码下拉选择器，当前支持以下股票：

| 代码   | 公司名称         |
|--------|------------------|
| NVDA   | NVIDIA           |
| TSLA   | Tesla            |
| AAPL   | Apple            |
| GOOGL  | Alphabet (Google)|
| KO     | Coca-Cola        |
| MSFT   | Microsoft        |
| AMZN   | Amazon           |

选择器支持筛选和自定义输入，切换股票时会重新加载三个面板的数据。

### 2. 三时间维度面板

页面垂直排列三个独立面板，分别展示近 1 年、2 年、3 年的 PE 数据：

- **近 1 年**：数据范围为最近 365 天
- **近 2 年**：数据范围为最近 730 天
- **近 3 年**：数据范围为最近 1095 天

每个面板包含：

- 当前 PE（TTM）数值
- 历史分位百分比（高 = 贵）
- 有效交易日数量
- 5 个分位标签（5%、25%、50%、75%、95%）
- 当前 PE 值高亮显示
- ECharts 交互图表

### 3. PE TTM 计算逻辑

滚动 PE（TTM）的计算方式为：

```
PE(TTM) = 每日收盘价 / 最近四个季度 EPS 之和
```

具体算法步骤：

1. **推导财报发布日期**：根据 EPS 条目的季度类型（Q1/Q2/Q3/Q4），映射到实际财报发布月份

| 季度 | 财报月-日 |
|------|-----------|
| Q1   | 05-01     |
| Q2   | 08-01     |
| Q3   | 11-01     |
| Q4   | 02-01（次年）|

2. **筛选可用 EPS**：在当前交易日之前已发布的最近 4 个季度 EPS
3. **求和计算 TTM EPS**：将 4 个季度 EPS 相加
4. **计算 PE**：收盘价除以 TTM EPS

仅当有效季度数 >= 4 且 TTM EPS > 0 时才计算 PE。

### 4. 历史分位数

每个面板计算并展示 5 个分位数阈值：

- **5% 分位**（绿色）：极度低估区域边界
- **25% 分位**（绿色）：较低估区域边界
- **50% 分位**（黄色）：中位数
- **75% 分位**（黄色）：较高估区域边界
- **95% 分位**（绿色）：极度高估区域边界

当前 PE 所在的分位决定了估值高低，颜色编码为：

- 绿色区域（低于 50% 分位）：偏低估
- 黄色区域（50%-75% 分位）：合理偏高
- 红色区域（高于 75% 分位）：偏高估

### 5. 数据来源

**价格数据**：通过 FMP API 获取每日收盘价

- 基础 URL：`https://financialmodelingprep.com/stable/historical-price-eod/full`
- 参数：symbol、from、to、apikey
- 超时时间：30 秒

**EPS 数据**：从 `eps.json` 文件加载，格式为：

```json
{
  "NVDA": [
    { "year": 2024, "quarter": "Q1", "eps": 6.12 },
    { "year": 2024, "quarter": "Q2", "eps": 6.90 },
    ...
  ]
}
```

EPS 数据也支持存储在 localStorage 中（key 格式：`pe_eps_${symbol}`）。

---

## 图表说明

每个面板的 ECharts 图表包含以下元素：

### 主折线
- 平滑曲线展示每日 PE(TTM)
- 面积渐变填充（蓝色系）
- 不显示单个数据点符号

### 分位参考线
- **10% 分位**（绿色虚线）
- **50% 分位**（黄色虚线）
- **90% 分位**（红色虚线）
- **当前 PE**（紫色实线，粗体）

### 分色背景区域
- **绿色区域**（10%-50%）：偏低估
- **黄色区域**（50%-90%）：中性区间
- **红色区域**（90%+）：偏高估

### 交互功能
- **缩放**：内置 dataZoom 滑块和滚轮缩放
- **悬停提示**：显示日期、PE 值、收盘价、TTM EPS、使用的季度明细
- **响应式**：监听窗口 resize 事件自动调整图表大小

---

## 核心函数

| 函数名 | 作用 |
|--------|------|
| `createPanel()` | 创建独立面板状态对象 |
| `loadEpsFromJson()` | 从 eps.json 加载 EPS 数据 |
| `loadFromStorage()` | 优先从 JSON 加载，fallback 到 localStorage |
| `onSymbolChange()` | 股票切换事件处理 |
| `deriveReportDate()` | 根据季度推导财报发布日期 |
| `calculateTtmEpsForDate()` | 计算指定日期的 TTM EPS |
| `buildDailyPeSeries()` | 构建每日 PE 序列 |
| `getPriceFmp()` | 调用 FMP API 获取历史价格 |
| `fetchPanel()` | 单面板数据获取 |
| `autoFetchAll()` | 并行获取三个面板数据 |
| `safeRenderChart()` | 安全渲染 ECharts 图表 |

---

## 组件结构

```
UsPeValuation.vue
├── template
│   ├── 顶部卡片（股票选择器）
│   │   └── el-form / el-select
│   └── 三面板行（panels-row）
│       ├── 近 1 年面板（panel1）
│       ├── 近 2 年面板（panel2）
│       └── 近 3 年面板（panel3）
│           └── 每个面板包含：
│               ├── el-statistic（当前 PE、分位、交易日数）
│               ├── el-tag（分位水平标签）
│               └── chart-container（ECharts 图表容器）
└── script
    ├── 状态管理（symbol、epsData、三个 panel）
    ├── 计算属性（CurrentPe、Percentile、PercentileLevels）
    ├── 数据获取（API 调用、EPS 加载）
    ├── 图表渲染（ECharts 配置）
    └── 生命周期（挂载/卸载/窗口 resize）
```

---

## 依赖项

| 依赖 | 用途 |
|------|------|
| Vue 3 Composition API | 响应式状态管理 |
| axios | HTTP 请求 |
| echarts | 数据可视化图表 |
| element-plus | UI 组件库 |
| eps.json | 本地 EPS 数据文件 |

---

## 使用前提

1. **EPS 数据必须存在**：在 `eps.json` 中为所选股票添加至少 4 个季度的 EPS 数据
2. **FMP API Key**：当前使用免费 API Key（`wQdt9jraXnrDCjOJVwELhblzjyBEXbI3`），可能有频率限制
3. **网络连通性**：需要能访问 `financialmodelingprep.com`

---

## 添加新股票 EPS 数据

在 `eps.json` 中添加新条目：

```json
{
  "新股票代码": [
    { "year": 2024, "quarter": "Q1", "eps": 1.00 },
    { "year": 2024, "quarter": "Q2", "eps": 1.20 },
    { "year": 2024, "quarter": "Q3", "eps": 1.30 },
    { "year": 2024, "quarter": "Q4", "eps": 1.50 }
  ]
}
```

然后在 `symbolOptions` 数组中添加股票代码即可。
