<template>
  <div class="valuation-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 style="margin: 0; font-size: 24px; padding: 0">
        加密项目估值分析工具
      </h1>
      <p class="subtitle">Crypto Project Valuation Tool</p>
    </div>

    <!-- 模式选择 -->
    <div class="mode-selection">
      <h2>📊 分析模式</h2>
      <div class="mode-options">
        <label class="mode-option">
          <input
            type="radio"
            v-model="analysisMode"
            value="single"
            class="mode-radio"
          />
          <span class="mode-label">单项目分析</span>
        </label>
        <label class="mode-option">
          <input
            type="radio"
            v-model="analysisMode"
            value="dual"
            class="mode-radio"
          />
          <span class="mode-label">双项目对比</span>
        </label>
      </div>
    </div>

    <!-- 项目输入区域 -->
    <div class="input-section">
      <!-- 项目A -->
      <div class="project-input">
        <h3>项目A数据</h3>
        <div class="project-name-input">
          <label>项目名称</label>
          <input
            v-model="projectA.name"
            type="text"
            placeholder="请输入项目名称，如：Uniswap"
            class="form-input project-name"
          />
        </div>
        <div class="metrics-grid">
          <div class="metric-item">
            <label>FDV (完全稀释估值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectA.fdv"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input type="radio" :value="1" v-model="projectA.fdvUnit" />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectA.fdvUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectA.fdvUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>MCap (当前市值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectA.mcap"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input type="radio" :value="1" v-model="projectA.mcapUnit" />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectA.mcapUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectA.mcapUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>TVL (总锁仓价值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectA.tvl"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input type="radio" :value="1" v-model="projectA.tvlUnit" />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectA.tvlUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectA.tvlUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>年化收入</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectA.revenue"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1"
                    v-model="projectA.revenueUnit"
                  />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectA.revenueUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectA.revenueUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>收入增长率季度 (%)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectA.growthRate"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <span class="unit-label">%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 项目B (仅双项目模式显示) -->
      <div class="project-input" v-if="analysisMode === 'dual'">
        <h3>项目B数据</h3>
        <div class="project-name-input">
          <label>项目名称</label>
          <input
            v-model="projectB.name"
            type="text"
            placeholder="请输入项目名称，如：SushiSwap"
            class="form-input project-name"
          />
        </div>
        <div class="metrics-grid">
          <div class="metric-item">
            <label>FDV (完全稀释估值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectB.fdv"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input type="radio" :value="1" v-model="projectB.fdvUnit" />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectB.fdvUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectB.fdvUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>MCap (当前市值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectB.mcap"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input type="radio" :value="1" v-model="projectB.mcapUnit" />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectB.mcapUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectB.mcapUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>TVL (总锁仓价值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectB.tvl"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input type="radio" :value="1" v-model="projectB.tvlUnit" />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectB.tvlUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectB.tvlUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>年化收入</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectB.revenue"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1"
                    v-model="projectB.revenueUnit"
                  />
                  <span>个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectB.revenueUnit"
                  />
                  <span>m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectB.revenueUnit"
                  />
                  <span>b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>收入增长率 (%)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectB.growthRate"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <span class="unit-label">%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成分析按钮 -->
    <div class="action-section">
      <button
        @click="generateAnalysis"
        class="analyze-btn"
        :disabled="isCalculating"
      >
        {{ isCalculating ? "分析中..." : "🔍 生成评估分析" }}
      </button>
    </div>

    <!-- 分析结果展示区 -->
    <div class="results-section" v-if="showResults">
      <!-- 单项目结果 -->
      <div v-if="analysisMode === 'single'" class="single-analysis">
        <h3>📈 {{ projectA.name || "项目A" }} 分析结果</h3>
        <div class="results-grid">
          <div
            class="result-item"
            v-for="(value, key) in analysisResult.ratios"
            :key="key"
          >
            <div class="metric-name">{{ getMetricName(key) }}</div>
            <div class="metric-value" :class="getValueClass(key, value)">
              {{ value.toFixed(2) }}
            </div>
            <div
              class="metric-assessment"
              :class="getAssessmentClass(analysisResult.assessments[key])"
            >
              {{ analysisResult.assessments[key] }}
            </div>
          </div>
        </div>

        <div class="text-analysis">
          <h4>📝 文字分析</h4>
          <p>{{ analysisResult.textAnalysis }}</p>
        </div>

        <div class="conclusion">
          <h4>🎯 综合结论</h4>
          <div
            class="conclusion-content"
            :class="getConclusionClass(analysisResult.overallConclusion)"
          >
            {{ analysisResult.overallConclusion }}
          </div>
        </div>
      </div>

      <!-- 双项目对比结果 -->
      <div v-if="analysisMode === 'dual'" class="dual-analysis">
        <h3>📊 对比分析结果</h3>

        <!-- CSS 百分比柱状图 -->
        <div class="comparison-charts">
          <div
            class="chart-item"
            v-for="(metric, key) in comparisonData"
            :key="key"
          >
            <div class="chart-title">{{ metric.name }}</div>
            <div class="chart-container">
              <!-- 项目A 柱状图 -->
              <div class="bar-wrapper">
                <div class="bar-label">{{ projectA.name || "项目A" }}</div>
                <div class="bar-container">
                  <div
                    class="bar-fill bar-a"
                    :style="{ width: metric.percentageA + '%' }"
                  >
                    <span class="bar-value">{{
                      metric.valueA.toFixed(2)
                    }}</span>
                  </div>
                </div>
              </div>

              <!-- 项目B 柱状图 -->
              <div class="bar-wrapper">
                <div class="bar-label">{{ projectB.name || "项目B" }}</div>
                <div class="bar-container">
                  <div
                    class="bar-fill bar-b"
                    :style="{ width: metric.percentageB + '%' }"
                  >
                    <span class="bar-value">{{
                      metric.valueB.toFixed(2)
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 对比分析文字 -->
        <div class="comparison-analysis">
          <h4>📝 对比分析</h4>
          <p>{{ comparisonAnalysis }}</p>
        </div>

        <!-- 综合结论 -->
        <div class="comparison-conclusion">
          <h4>🎯 综合结论</h4>
          <div
            class="conclusion-content"
            :class="getConclusionClass(comparisonConclusion)"
          >
            {{ comparisonConclusion }}
          </div>
        </div>
      </div>
    </div>

    <!-- 指标说明区 -->
    <div class="metrics-explanation">
      <h3>📚 指标说明</h3>
      <div class="explanation-grid">
        <div class="explanation-item">
          <h4>1. FDV/MCap（完全稀释估值 / 流通市值）</h4>
          <p>
            <strong>含义：</strong
            >反映流通市值与完全稀释估值的关系，衡量潜在稀释风险。
          </p>
          <p>
            <strong>评估区间：</strong
            >1–1.5健康；1.5–3可接受；3–5谨慎；5–10高风险；>10极高风险。
          </p>
        </div>

        <div class="explanation-item">
          <h4>2. MCap/TVL（流通市值 / 锁仓资金量）</h4>
          <p><strong>含义：</strong>衡量市值与资金沉淀的匹配度。</p>
          <p>
            <strong>评估区间：</strong
            ><1可能低估；1–3合理；3–5偏高估；5–10高风险；>10极端高估。
          </p>
        </div>

        <div class="explanation-item">
          <h4>3. MCap/年化收入</h4>
          <p>
            <strong>含义：</strong
            >投资人愿意为每1美元收入支付多少市值，反映估值水平。
          </p>
          <p>
            <strong>评估区间：</strong>DEX 10–30合理；公链
            30–100合理，大于150高估；稳定币 5–15合理；CEX 5–20合理；新兴赛道
            40+高风险。
          </p>
        </div>

        <div class="explanation-item">
          <h4>4. FDV/TVL（DeFi专用）</h4>
          <p><strong>含义：</strong>估值与管理资产规模的匹配度。</p>
          <p>
            <strong>评估区间：</strong
            ><0.5显著低估；0.5–1.5合理；1.5–3偏高；>3高估警示。
          </p>
        </div>

        <div class="explanation-item">
          <h4>5. 收入增长率（季度环比）</h4>
          <p><strong>含义：</strong>反映项目的成长性与估值合理性。</p>
          <p>
            <strong>评估区间：</strong
            >>50%爆发式增长；10–50%健康增长；<10%停滞/成熟。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";

// 响应式数据
const analysisMode = ref("single");
const isCalculating = ref(false);
const showResults = ref(false);

// 项目数据结构
interface ProjectData {
  name: string;
  fdv: number;
  fdvUnit: number;
  mcap: number;
  mcapUnit: number;
  tvl: number;
  tvlUnit: number;
  revenue: number;
  revenueUnit: number;
  growthRate: number;
}

// 分析结果结构
interface AnalysisResult {
  ratios: {
    fdvMcap: number;
    mcapTvl: number;
    mcapRevenue: number;
    fdvTvl: number;
    growthRate: number;
  };
  assessments: {
    fdvMcap: string;
    mcapTvl: string;
    mcapRevenue: string;
    fdvTvl: string;
    growthRate: string;
  };
  overallConclusion: string;
  textAnalysis: string;
}

// 初始化项目数据
const projectA = ref<ProjectData>({
  name: "",
  fdv: 0,
  fdvUnit: 1000000,
  mcap: 0,
  mcapUnit: 1000000,
  tvl: 0,
  tvlUnit: 1000000,
  revenue: 0,
  revenueUnit: 1000000,
  growthRate: 0,
});

const projectB = ref<ProjectData>({
  name: "",
  fdv: 0,
  fdvUnit: 1000000,
  mcap: 0,
  mcapUnit: 1000000,
  tvl: 0,
  tvlUnit: 1000000,
  revenue: 0,
  revenueUnit: 1000000,
  growthRate: 0,
});

// 分析结果
const analysisResult = ref<AnalysisResult>({
  ratios: {
    fdvMcap: 0,
    mcapTvl: 0,
    mcapRevenue: 0,
    fdvTvl: 0,
    growthRate: 0,
  },
  assessments: {
    fdvMcap: "",
    mcapTvl: "",
    mcapRevenue: "",
    fdvTvl: "",
    growthRate: "",
  },
  overallConclusion: "",
  textAnalysis: "",
});

// 对比数据
const comparisonAnalysis = ref("");
const comparisonConclusion = ref("");

// 计算估值比率
const calculateRatios = (project: ProjectData) => {
  const fdv = project.fdv * project.fdvUnit;
  const mcap = project.mcap * project.mcapUnit;
  const tvl = project.tvl * project.tvlUnit;
  const revenue = project.revenue * project.revenueUnit;
  const growthRate = project.growthRate;

  return {
    fdvMcap: mcap > 0 ? fdv / mcap : 0,
    mcapTvl: tvl > 0 ? mcap / tvl : 0,
    mcapRevenue: revenue > 0 ? mcap / revenue : 0,
    fdvTvl: tvl > 0 ? fdv / tvl : 0,
    growthRate: growthRate,
  };
};

// 评估指标状态
const assessMetric = (key: string, value: number) => {
  const thresholds = {
    fdvMcap: { low: 1, medium: 1.5, high: 3, veryHigh: 5 },
    mcapTvl: { low: 1, medium: 3, high: 5, veryHigh: 10 },
    mcapRevenue: { low: 10, medium: 30, high: 100, veryHigh: 150 },
    fdvTvl: { low: 0.5, medium: 1.5, high: 3, veryHigh: 5 },
    growthRate: { low: 10, medium: 50, high: 100, veryHigh: 200 },
  };

  const threshold = thresholds[key as keyof typeof thresholds];
  if (!threshold) return "未知";

  if (value < threshold.low) return "可能低估";
  if (value < threshold.medium) return "合理";
  if (value < threshold.high) return "偏高";
  if (value < threshold.veryHigh) return "高估警示";
  return "极高风险";
};

// 生成文字分析
const generateTextAnalysis = (ratios: any, assessments: any) => {
  let analysis = "";

  // FDV/MCap分析
  if (ratios.fdvMcap > 0) {
    if (assessments.fdvMcap === "健康") {
      analysis += `FDV/MCap比率为${ratios.fdvMcap.toFixed(
        2
      )}，处于健康区间，稀释风险较低。`;
    } else if (assessments.fdvMcap === "合理") {
      analysis += `FDV/MCap比率为${ratios.fdvMcap.toFixed(
        2
      )}，处于合理区间，存在一定稀释风险。`;
    } else {
      analysis += `FDV/MCap比率为${ratios.fdvMcap.toFixed(2)}，${
        assessments.fdvMcap
      }，需要关注稀释风险。`;
    }
  }

  // MCap/TVL分析
  if (ratios.mcapTvl > 0) {
    analysis += ` MCap/TVL比率为${ratios.mcapTvl.toFixed(2)}，${
      assessments.mcapTvl
    }。`;
  }

  // MCap/收入分析
  if (ratios.mcapRevenue > 0) {
    analysis += ` MCap/年化收入比率为${ratios.mcapRevenue.toFixed(2)}，${
      assessments.mcapRevenue
    }。`;
  }

  // 收入增长率分析
  if (ratios.growthRate > 0) {
    analysis += ` 收入增长率为${ratios.growthRate.toFixed(1)}%，${
      assessments.growthRate
    }。`;
  }

  return analysis;
};

// 生成综合结论
const generateOverallConclusion = (assessments: any) => {
  const riskCount = Object.values(assessments).filter(
    (assessment) =>
      assessment === "极高风险" ||
      assessment === "高估警示" ||
      assessment === "偏高"
  ).length;

  const healthyCount = Object.values(assessments).filter(
    (assessment) => assessment === "合理" || assessment === "可能低估"
  ).length;

  if (riskCount >= 3) {
    return "估值偏高，存在较高风险，建议谨慎投资";
  } else if (healthyCount >= 3) {
    return "估值相对合理，具备一定投资价值";
  } else {
    return "估值水平中等，需要进一步分析项目基本面";
  }
};

// 计算对比数据
const comparisonData = computed(() => {
  if (analysisMode.value !== "dual") return [];

  const ratiosA = calculateRatios(projectA.value);
  const ratiosB = calculateRatios(projectB.value);

  const metrics = [
    { key: "fdvMcap", name: "FDV/MCap" },
    { key: "mcapTvl", name: "MCap/TVL" },
    { key: "mcapRevenue", name: "MCap/年化收入" },
    { key: "fdvTvl", name: "FDV/TVL" },
    { key: "growthRate", name: "收入增长率" },
  ];

  return metrics.map((metric) => {
    const valueA = ratiosA[metric.key as keyof typeof ratiosA];
    const valueB = ratiosB[metric.key as keyof typeof ratiosB];

    // 计算百分比（基于较大值）
    const maxValue = Math.max(valueA, valueB);
    const percentageA = maxValue > 0 ? (valueA / maxValue) * 100 : 0;
    const percentageB = maxValue > 0 ? (valueB / maxValue) * 100 : 0;

    return {
      name: metric.name,
      valueA,
      valueB,
      percentageA,
      percentageB,
    };
  });
});

// 生成分析
const generateAnalysis = async () => {
  isCalculating.value = true;
  showResults.value = false;

  // 模拟计算延迟
  await new Promise((resolve) => setTimeout(resolve, 1000));

  if (analysisMode.value === "single") {
    // 单项目分析
    const ratios = calculateRatios(projectA.value);
    const assessments = {
      fdvMcap: assessMetric("fdvMcap", ratios.fdvMcap),
      mcapTvl: assessMetric("mcapTvl", ratios.mcapTvl),
      mcapRevenue: assessMetric("mcapRevenue", ratios.mcapRevenue),
      fdvTvl: assessMetric("fdvTvl", ratios.fdvTvl),
      growthRate: assessMetric("growthRate", ratios.growthRate),
    };

    analysisResult.value = {
      ratios,
      assessments,
      overallConclusion: generateOverallConclusion(assessments),
      textAnalysis: generateTextAnalysis(ratios, assessments),
    };
  } else {
    // 双项目对比分析
    const ratiosA = calculateRatios(projectA.value);
    const ratiosB = calculateRatios(projectB.value);

    // 生成对比分析
    comparisonAnalysis.value = generateComparisonAnalysis(ratiosA, ratiosB);
    comparisonConclusion.value = generateComparisonConclusion(ratiosA, ratiosB);
  }

  isCalculating.value = false;
  showResults.value = true;
};

// 生成对比分析
const generateComparisonAnalysis = (ratiosA: any, ratiosB: any) => {
  const projectAName = projectA.value.name || "项目A";
  const projectBName = projectB.value.name || "项目B";

  let analysis = "通过对比分析发现：";

  // 比较各个指标
  if (ratiosA.fdvMcap < ratiosB.fdvMcap) {
    analysis += ` ${projectAName}在稀释风险控制上更优；`;
  } else {
    analysis += ` ${projectBName}在稀释风险控制上更优；`;
  }

  if (ratiosA.mcapTvl < ratiosB.mcapTvl) {
    analysis += ` ${projectAName}的市值与TVL匹配度更好；`;
  } else {
    analysis += ` ${projectBName}的市值与TVL匹配度更好；`;
  }

  if (ratiosA.mcapRevenue < ratiosB.mcapRevenue) {
    analysis += ` ${projectAName}的市值与收入匹配度更好；`;
  } else {
    analysis += ` ${projectBName}的市值与收入匹配度更好；`;
  }

  if (ratiosA.growthRate > ratiosB.growthRate) {
    analysis += ` ${projectAName}的收入增长率更高，成长性更强。`;
  } else {
    analysis += ` ${projectBName}的收入增长率更高，成长性更强。`;
  }

  return analysis;
};

// 生成对比结论
const generateComparisonConclusion = (ratiosA: any, ratiosB: any) => {
  const projectAName = projectA.value.name || "项目A";
  const projectBName = projectB.value.name || "项目B";

  let scoreA = 0;
  let scoreB = 0;

  // 评分逻辑（数值越小越好，除了增长率）
  const metrics = ["fdvMcap", "mcapTvl", "mcapRevenue", "fdvTvl"];

  metrics.forEach((metric) => {
    if (ratiosA[metric] < ratiosB[metric]) scoreA++;
    else scoreB++;
  });

  // 增长率评分（数值越大越好）
  if (ratiosA.growthRate > ratiosB.growthRate) scoreA++;
  else scoreB++;

  if (scoreA > scoreB) {
    return `${projectAName}整体估值更合理，投资价值更高`;
  } else if (scoreB > scoreA) {
    return `${projectBName}整体估值更合理，投资价值更高`;
  } else {
    return "两个项目估值水平相当，需要结合其他因素综合判断";
  }
};

// 获取指标名称
const getMetricName = (key: string) => {
  const names: { [key: string]: string } = {
    fdvMcap: "FDV/MCap",
    mcapTvl: "MCap/TVL",
    mcapRevenue: "MCap/年化收入",
    fdvTvl: "FDV/TVL",
    growthRate: "收入增长率",
  };
  return names[key] || key;
};

// 获取数值样式类
const getValueClass = (key: string, value: number) => {
  const assessment = assessMetric(key, value);
  if (assessment === "合理" || assessment === "可能低估")
    return "value-healthy";
  if (
    assessment === "偏高" ||
    assessment === "高估警示" ||
    assessment === "极高风险"
  )
    return "value-risky";
  return "value-neutral";
};

// 获取评估样式类
const getAssessmentClass = (assessment: string) => {
  if (assessment === "合理" || assessment === "可能低估")
    return "assessment-healthy";
  if (
    assessment === "偏高" ||
    assessment === "高估警示" ||
    assessment === "极高风险"
  )
    return "assessment-risky";
  return "assessment-neutral";
};

// 获取结论样式类
const getConclusionClass = (conclusion: string) => {
  if (conclusion.includes("合理") || conclusion.includes("价值"))
    return "conclusion-positive";
  if (conclusion.includes("风险") || conclusion.includes("谨慎"))
    return "conclusion-warning";
  return "conclusion-neutral";
};

// 监听模式变化
watch(analysisMode, () => {
  showResults.value = false;
});
</script>

<style scoped>
.valuation-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.subtitle {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

.mode-selection {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.mode-selection h2 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.mode-options {
  display: flex;
  gap: 20px;
}

.mode-option {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.mode-radio {
  margin-right: 8px;
}

.mode-label {
  font-weight: 500;
  color: #2c3e50;
}

.input-section {
  margin-bottom: 30px;
}

.project-input {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.project-input h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
}

.project-name-input {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.project-name-input label {
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.project-name {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
}

.metric-item label {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.unit-radio-group {
  display: flex;
  gap: 8px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-item input {
  margin-right: 4px;
}

.unit-label {
  color: #7f8c8d;
  font-size: 14px;
}

.action-section {
  text-align: center;
  margin: 30px 0;
}

.analyze-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.analyze-btn:hover:not(:disabled) {
  background: #0056b3;
}

.analyze-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.results-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.results-section h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.result-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  text-align: center;
}

.metric-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.value-healthy {
  color: #28a745;
}

.value-risky {
  color: #dc3545;
}

.value-neutral {
  color: #6c757d;
}

.metric-assessment {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.assessment-healthy {
  background: #d4edda;
  color: #155724;
}

.assessment-risky {
  background: #f8d7da;
  color: #721c24;
}

.assessment-neutral {
  background: #d1ecf1;
  color: #0c5460;
}

.text-analysis,
.conclusion {
  margin-top: 20px;
}

.text-analysis h4,
.conclusion h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.conclusion-content {
  padding: 15px;
  border-radius: 6px;
  font-weight: 500;
}

.conclusion-positive {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.conclusion-warning {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.conclusion-neutral {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* CSS 百分比柱状图样式 */
.comparison-charts {
  display: grid;
  gap: 25px;
  margin: 20px 0;
}

.chart-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
  text-align: center;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-wrapper {
  display: flex;
  align-items: center;
  gap: 15px;
}

.bar-label {
  min-width: 80px;
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
}

.bar-container {
  flex: 1;
  height: 30px;
  background: #e9ecef;
  border-radius: 15px;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 15px;
  position: relative;
  transition: width 0.8s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
}

.bar-a {
  background: linear-gradient(90deg, #5470c6, #3b4f8a);
}

.bar-b {
  background: linear-gradient(90deg, #91cc75, #6ba85a);
}

.bar-value {
  color: white;
  font-weight: 600;
  font-size: 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.comparison-analysis,
.comparison-conclusion {
  margin-top: 20px;
}

.comparison-analysis h4,
.comparison-conclusion h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.metrics-explanation {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.metrics-explanation h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.explanation-grid {
  display: grid;
  gap: 20px;
}

.explanation-item {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.explanation-item h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
}

.explanation-item p {
  margin: 5px 0;
  color: #6c757d;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .mode-options {
    flex-direction: column;
    gap: 10px;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .bar-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .bar-label {
    min-width: auto;
    text-align: center;
  }

  .bar-container {
    height: 25px;
  }

  .bar-value {
    font-size: 11px;
  }
}
</style>
