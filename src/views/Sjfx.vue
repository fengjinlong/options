<template>
  <div class="valuation-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 style="font-size: 24px; font-weight: bold; margin: 0">
        加密项目估值分析工具
      </h1>
      <p class="subtitle">Crypto Project Valuation Tool</p>
    </div>

    <!-- 数据输入区域 -->
    <div class="input-section">
      <div class="section-title">
        <h2>📊 项目数据输入</h2>
      </div>

      <!-- 项目基本信息 -->
      <div class="input-group">
        <h3>项目基本信息</h3>
        <div class="form-row">
          <div class="form-item">
            <label>项目名称</label>
            <input
              v-model="projectData.name"
              type="text"
              placeholder="请输入项目名称"
              class="form-input"
            />
          </div>
          <div class="form-item">
            <label>项目类型</label>
            <select v-model="projectData.type" class="form-select">
              <option value="">请选择项目类型</option>
              <option value="defi">DeFi</option>
              <option value="dex">DEX</option>
              <option value="blockchain">公链</option>
              <option value="stablecoin">稳定币</option>
              <option value="cex">CEX</option>
              <option value="other">其他</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 核心财务指标 -->
      <div class="input-group">
        <h3>核心财务指标</h3>
        <div class="metrics-grid">
          <div class="metric-item">
            <label>FDV (完全稀释估值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectData.fdv"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1"
                    v-model="projectData.fdvUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectData.fdvUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectData.fdvUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>MCap (当前市值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectData.mcap"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1"
                    v-model="projectData.mcapUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectData.mcapUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectData.mcapUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>TVL (总锁仓价值)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectData.tvl"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1"
                    v-model="projectData.tvlUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectData.tvlUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectData.tvlUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>年化收入</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectData.revenue"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <div class="unit-radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1"
                    v-model="projectData.revenueUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">个</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000"
                    v-model="projectData.revenueUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">m</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    :value="1000000000"
                    v-model="projectData.revenueUnit"
                    class="radio-input"
                  />
                  <span class="radio-label">b</span>
                </label>
              </div>
            </div>
          </div>

          <div class="metric-item">
            <label>收入增长率季度 (%)</label>
            <div class="input-with-unit">
              <input
                v-model.number="projectData.revenueGrowth"
                type="number"
                placeholder="0"
                class="form-input"
              />
              <span class="unit-text">%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 生成按钮 -->
      <div class="action-section">
        <button
          @click="calculateValuation"
          :disabled="!isFormValid"
          class="calculate-btn"
        >
          🔍 生成估值分析
        </button>
      </div>
    </div>

    <!-- 分析结果展示区 -->
    <div v-if="analysisResult" class="results-section">
      <div class="section-title">
        <h2>📈 分析结果</h2>
      </div>

      <!-- 计算结果 -->
      <div class="results-grid">
        <div class="result-item">
          <div class="metric-name">FDV/MCap</div>
          <div
            class="metric-value"
            :class="getStatusClass(analysisResult.fdvMcapStatus)"
          >
            {{ analysisResult.fdvMcapRatio.toFixed(2) }}
          </div>
          <div class="metric-status">{{ analysisResult.fdvMcapStatus }}</div>
        </div>

        <div class="result-item">
          <div class="metric-name">MCap/TVL</div>
          <div
            class="metric-value"
            :class="getStatusClass(analysisResult.mcapTvlStatus)"
          >
            {{ analysisResult.mcapTvlRatio.toFixed(2) }}
          </div>
          <div class="metric-status">{{ analysisResult.mcapTvlStatus }}</div>
        </div>

        <div class="result-item">
          <div class="metric-name">MCap/年化收入</div>
          <div
            class="metric-value"
            :class="getStatusClass(analysisResult.mcapRevenueStatus)"
          >
            {{ analysisResult.mcapRevenueRatio.toFixed(2) }}
          </div>
          <div class="metric-status">
            {{ analysisResult.mcapRevenueStatus }}
          </div>
        </div>

        <div class="result-item">
          <div class="metric-name">FDV/TVL</div>
          <div
            class="metric-value"
            :class="getStatusClass(analysisResult.fdvTvlStatus)"
          >
            {{ analysisResult.fdvTvlRatio.toFixed(2) }}
          </div>
          <div class="metric-status">{{ analysisResult.fdvTvlStatus }}</div>
        </div>

        <div class="result-item">
          <div class="metric-name">收入增长率</div>
          <div
            class="metric-value"
            :class="getStatusClass(analysisResult.revenueGrowthStatus)"
          >
            {{ analysisResult.revenueGrowth }}%
          </div>
          <div class="metric-status">
            {{ analysisResult.revenueGrowthStatus }}
          </div>
        </div>
      </div>

      <!-- 综合结论 -->
      <div class="conclusion-section">
        <div class="conclusion-card">
          <h3>🎯 综合估值结论</h3>
          <div class="conclusion-content">
            <div class="conclusion-item">
              <span class="label">项目估值状态:</span>
              <span
                class="value"
                :class="getOverallStatusClass(analysisResult.overallStatus)"
              >
                {{ analysisResult.overallStatus }}
              </span>
            </div>
            <div class="conclusion-item">
              <span class="label">风险等级:</span>
              <span
                class="value"
                :class="getRiskClass(analysisResult.riskLevel)"
              >
                {{ analysisResult.riskLevel }}
              </span>
            </div>
            <div class="conclusion-item">
              <span class="label">投资建议:</span>
              <span class="value">{{ analysisResult.investmentAdvice }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 指标说明区域 -->
    <div class="explanation-section">
      <div class="section-title">
        <h2>📚 指标说明</h2>
      </div>

      <div class="explanation-content">
        <div class="explanation-item">
          <h4>1. FDV/MCap (稀释风险指标)</h4>
          <ul>
            <li><span class="range good">1.0-1.5:</span> 健康，稀释风险低</li>
            <li>
              <span class="range acceptable">1.5-3.0:</span>
              可接受，需关注解锁节奏
            </li>
            <li>
              <span class="range caution">3.0-5.0:</span> 需谨慎，存在锁仓风险
            </li>
            <li>
              <span class="range high">5.0-10:</span> 高风险，未来抛压明显
            </li>
            <li><span class="range extreme">>10:</span> 极高风险，严重稀释</li>
          </ul>
        </div>

        <div class="explanation-item">
          <h4>2. MCap/TVL (市值与资产匹配度)</h4>
          <ul>
            <li><span class="range good"><1:</span> 可能低估，TVL质量高</li>
            <li><span class="range good">1-3:</span> 健康/合理</li>
            <li><span class="range caution">3-5:</span> 偏高估</li>
            <li><span class="range high">5-10:</span> 高风险</li>
            <li><span class="range extreme">>10:</span> 极端高估</li>
          </ul>
        </div>

        <div class="explanation-item">
          <h4>3. MCap/年化收入 (估值对比赛道水平)</h4>
          <ul>
            <li>
              <span class="range good">DEX/DeFi:</span>
              10-30合理，<10低估，>40高估
            </li>
            <li><span class="range good">公链:</span> 30-100合理，>150高估</li>
            <li><span class="range good">稳定币:</span> 5-15合理</li>
            <li><span class="range good">CEX:</span> 5-20合理</li>
            <li><span class="range high">新兴赛道:</span> 40+高风险溢价</li>
          </ul>
        </div>

        <div class="explanation-item">
          <h4>4. FDV/TVL (估值与资产规模关系)</h4>
          <ul>
            <li><span class="range good"><0.5:</span> 显著低估</li>
            <li><span class="range good">0.5-1.5:</span> 合理</li>
            <li><span class="range caution">1.5-3:</span> 偏高</li>
            <li><span class="range high">>3:</span> 高估警示</li>
          </ul>
        </div>

        <div class="explanation-item">
          <h4>5. 收入增长率 (项目成长性参考)</h4>
          <ul>
            <li><span class="range good">>50%:</span> 爆发式增长，估值可高</li>
            <li><span class="range good">10%-50%:</span> 健康增长</li>
            <li>
              <span class="range caution"><10%:</span> 停滞或成熟，若估值高→高估
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

// 定义分析结果类型
interface AnalysisResult {
  fdvMcapRatio: number;
  mcapTvlRatio: number;
  mcapRevenueRatio: number;
  fdvTvlRatio: number;
  revenueGrowth: number;
  fdvMcapStatus: string;
  mcapTvlStatus: string;
  mcapRevenueStatus: string;
  fdvTvlStatus: string;
  revenueGrowthStatus: string;
  overallStatus: string;
  riskLevel: string;
  investmentAdvice: string;
}

// 项目数据
const projectData = ref({
  name: "",
  type: "defi",
  fdv: 0,
  fdvUnit: 1000000,
  mcap: 0,
  mcapUnit: 1000000,
  tvl: 0,
  tvlUnit: 1000000,
  revenue: 0,
  revenueUnit: 1000000,
  revenueGrowth: 0,
});

// 分析结果
const analysisResult = ref<AnalysisResult | null>(null);

// 表单验证
const isFormValid = computed(() => {
  return (
    projectData.value.fdv > 0 &&
    projectData.value.mcap > 0 &&
    projectData.value.tvl > 0 &&
    projectData.value.revenue > 0
  );
});

// 单位转换函数
const convertToMillion = (value: number, unit: number) => {
  return (value * unit) / 1000000;
};

// 计算估值指标
const calculateValuation = () => {
  if (!isFormValid.value) return;

  // 转换单位到百万
  const fdv = convertToMillion(
    projectData.value.fdv,
    projectData.value.fdvUnit
  );
  const mcap = convertToMillion(
    projectData.value.mcap,
    projectData.value.mcapUnit
  );
  const tvl = convertToMillion(
    projectData.value.tvl,
    projectData.value.tvlUnit
  );
  const revenue = convertToMillion(
    projectData.value.revenue,
    projectData.value.revenueUnit
  );

  // 计算比率
  const fdvMcapRatio = fdv / mcap;
  const mcapTvlRatio = mcap / tvl;
  const mcapRevenueRatio = mcap / revenue;
  const fdvTvlRatio = fdv / tvl;

  // 判断状态
  const fdvMcapStatus = evaluateFdvMcap(fdvMcapRatio);
  const mcapTvlStatus = evaluateMcapTvl(mcapTvlRatio);
  const mcapRevenueStatus = evaluateMcapRevenue(
    mcapRevenueRatio,
    projectData.value.type
  );
  const fdvTvlStatus = evaluateFdvTvl(fdvTvlRatio);
  const revenueGrowthStatus = evaluateRevenueGrowth(
    projectData.value.revenueGrowth
  );

  // 综合评估
  const overallStatus = calculateOverallStatus({
    fdvMcapStatus,
    mcapTvlStatus,
    mcapRevenueStatus,
    fdvTvlStatus,
    revenueGrowthStatus,
  });

  const riskLevel = calculateRiskLevel({
    fdvMcapStatus,
    mcapTvlStatus,
    mcapRevenueStatus,
    fdvTvlStatus,
    revenueGrowthStatus,
  });

  const investmentAdvice = generateInvestmentAdvice(overallStatus);

  analysisResult.value = {
    fdvMcapRatio,
    mcapTvlRatio,
    mcapRevenueRatio,
    fdvTvlRatio,
    revenueGrowth: projectData.value.revenueGrowth,
    fdvMcapStatus,
    mcapTvlStatus,
    mcapRevenueStatus,
    fdvTvlStatus,
    revenueGrowthStatus,
    overallStatus,
    riskLevel,
    investmentAdvice,
  };
};

// 评估函数
const evaluateFdvMcap = (ratio: number) => {
  if (ratio <= 1.5) return "健康";
  if (ratio <= 3) return "可接受";
  if (ratio <= 5) return "需谨慎";
  if (ratio <= 10) return "高风险";
  return "极高风险";
};

const evaluateMcapTvl = (ratio: number) => {
  if (ratio < 1) return "可能低估";
  if (ratio <= 3) return "健康";
  if (ratio <= 5) return "偏高估";
  if (ratio <= 10) return "高风险";
  return "极端高估";
};

const evaluateMcapRevenue = (ratio: number, type: string) => {
  const standards: Record<string, { good: [number, number]; caution: number }> =
    {
      defi: { good: [10, 30], caution: 40 },
      dex: { good: [10, 30], caution: 40 },
      blockchain: { good: [30, 100], caution: 150 },
      stablecoin: { good: [5, 15], caution: 20 },
      cex: { good: [5, 20], caution: 30 },
      other: { good: [20, 50], caution: 60 },
    };

  const standard = standards[type] || standards.other;

  if (ratio < standard.good[0]) return "低估";
  if (ratio <= standard.good[1]) return "合理";
  if (ratio <= standard.caution) return "偏高";
  return "高估";
};

const evaluateFdvTvl = (ratio: number) => {
  if (ratio < 0.5) return "显著低估";
  if (ratio <= 1.5) return "合理";
  if (ratio <= 3) return "偏高";
  return "高估警示";
};

const evaluateRevenueGrowth = (growth: number) => {
  if (growth > 50) return "爆发式增长";
  if (growth >= 10) return "健康增长";
  return "增长缓慢";
};

// 综合状态计算
const calculateOverallStatus = (statuses: Record<string, string>) => {
  const goodCount = Object.values(statuses).filter((status) =>
    ["健康", "合理", "可能低估", "显著低估"].includes(status)
  ).length;

  const cautionCount = Object.values(statuses).filter((status) =>
    ["可接受", "偏高", "需谨慎"].includes(status)
  ).length;

  const riskCount = Object.values(statuses).filter((status) =>
    ["高风险", "高估", "高估警示", "极端高估", "极高风险"].includes(status)
  ).length;

  if (riskCount > cautionCount + goodCount) return "高估";
  if (cautionCount > goodCount) return "偏高估";
  if (goodCount > cautionCount + riskCount) return "合理估值";
  return "需关注";
};

// 风险等级计算
const calculateRiskLevel = (statuses: Record<string, string>) => {
  const riskCount = Object.values(statuses).filter((status) =>
    ["高风险", "高估", "高估警示", "极端高估", "极高风险"].includes(status)
  ).length;

  if (riskCount >= 3) return "高";
  if (riskCount >= 1) return "中";
  return "低";
};

// 投资建议生成
const generateInvestmentAdvice = (overallStatus: string) => {
  if (overallStatus === "高估") return "建议谨慎投资，等待更好的入场时机";
  if (overallStatus === "偏高估") return "可考虑小仓位投资，密切关注项目发展";
  if (overallStatus === "合理估值") return "可考虑投资，但需关注收入增长趋势";
  if (overallStatus === "需关注") return "需要更多信息进行判断";
  return "建议进一步分析项目基本面";
};

// 状态样式类
const getStatusClass = (status: string) => {
  if (["健康", "合理", "可能低估", "显著低估"].includes(status))
    return "status-good";
  if (["可接受", "偏高", "需谨慎"].includes(status)) return "status-caution";
  return "status-risk";
};

const getOverallStatusClass = (status: string) => {
  if (status === "合理估值") return "overall-good";
  if (status === "偏高估") return "overall-caution";
  return "overall-risk";
};

const getRiskClass = (risk: string) => {
  if (risk === "低") return "risk-low";
  if (risk === "中") return "risk-medium";
  return "risk-high";
};
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
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.section-title {
  margin-bottom: 20px;
}

.section-title h2 {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.input-section {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.input-group {
  margin-bottom: 30px;
}

.input-group h3 {
  color: #34495e;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
}

.form-item label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #2c3e50;
}

.form-input,
.form-select {
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3498db;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.input-with-unit {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 50%;
}

.input-with-unit .form-input {
  width: 100%;
}

.unit-radio-group {
  display: flex;
  gap: 8px;
  justify-content: center;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s;
  background: white;
  border: 1px solid #e1e8ed;
}

.radio-item:hover {
  background: #e3f2fd;
  border-color: #3498db;
}

.radio-item:has(.radio-input:checked) {
  background: #3498db;
  border-color: #2980b9;
  color: white;
}

.radio-input {
  display: none;
}

.radio-label {
  font-weight: 600;
  font-size: 14px;
  user-select: none;
}

.unit-text {
  display: flex;
  align-items: center;
  padding: 0 15px;
  background: #ecf0f1;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-weight: 600;
  color: #2c3e50;
  height: 48px;
  justify-content: center;
}

.action-section {
  text-align: center;
  margin-top: 30px;
}

.calculate-btn {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  padding: 15px 40px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.calculate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.calculate-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.results-section {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.result-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #3498db;
}

.metric-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.metric-status {
  font-size: 0.9rem;
  font-weight: 600;
}

.status-good {
  color: #27ae60;
}

.status-caution {
  color: #f39c12;
}

.status-risk {
  color: #e74c3c;
}

.conclusion-section {
  margin-top: 30px;
}

.conclusion-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
}

.conclusion-card h3 {
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.conclusion-content {
  display: grid;
  gap: 15px;
}

.conclusion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.conclusion-item:last-child {
  border-bottom: none;
}

.conclusion-item .label {
  font-weight: 600;
}

.conclusion-item .value {
  font-weight: bold;
  padding: 5px 15px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
}

.overall-good {
  background: rgba(39, 174, 96, 0.8) !important;
}

.overall-caution {
  background: rgba(243, 156, 18, 0.8) !important;
}

.overall-risk {
  background: rgba(231, 76, 60, 0.8) !important;
}

.risk-low {
  background: rgba(39, 174, 96, 0.8) !important;
}

.risk-medium {
  background: rgba(243, 156, 18, 0.8) !important;
}

.risk-high {
  background: rgba(231, 76, 60, 0.8) !important;
}

.explanation-section {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.explanation-content {
  display: grid;
  gap: 25px;
}

.explanation-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.explanation-item h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.explanation-item ul {
  list-style: none;
  padding: 0;
}

.explanation-item li {
  padding: 8px 0;
  border-bottom: 1px solid #ecf0f1;
}

.explanation-item li:last-child {
  border-bottom: none;
}

.range {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 10px;
}

.range.good {
  background: #d5f4e6;
  color: #27ae60;
}

.range.acceptable {
  background: #fef5e7;
  color: #f39c12;
}

.range.caution {
  background: #fdeaea;
  color: #e67e22;
}

.range.high {
  background: #fadbd8;
  color: #e74c3c;
}

.range.extreme {
  background: #fadbd8;
  color: #c0392b;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .conclusion-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .unit-radio-group {
    flex-wrap: wrap;
  }

  .input-with-unit {
    max-width: 100%;
  }
}
</style>
