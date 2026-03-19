<template>
  <div class="dcf-container">
    <!-- 第一屏：参数输入 + 估值结果 -->
    <div class="main-section">
      <!-- 左侧：参数输入 -->
      <div class="input-section">
        <div class="section-title">
          <h2>📊 参数输入</h2>
        </div>
        <div class="input-group">
          <div class="form-grid">
            <div class="form-item">
              <label>当前价格 (P)</label>
              <div class="input-with-unit">
                <input v-model.number="params.currentPrice" type="number" step="0.01" min="0" class="form-input" />
                <span class="unit-text">元</span>
              </div>
            </div>

            <div class="form-item">
              <label>自由现金流 (FCF)</label>
              <div class="input-with-unit">
                <input v-model.number="params.fcf" type="number" step="0.01" min="0" class="form-input" />
                <div class="unit-selector">
                  <button :class="{ active: params.fcfUnit === 1 }" @click="params.fcfUnit = 1" type="button">元</button>
                  <button :class="{ active: params.fcfUnit === 100000000 }" @click="params.fcfUnit = 100000000" type="button">亿</button>
                </div>
              </div>
            </div>

            <div class="form-item">
              <label>折现率 (r)</label>
              <div class="input-with-unit">
                <input v-model.number="params.discountRate" type="number" step="0.1" min="0" max="100" class="form-input" />
                <span class="unit-text">%</span>
              </div>
            </div>

            <div class="form-item">
              <label>增长率 (g)</label>
              <div class="input-with-unit">
                <input v-model.number="params.growthRate" type="number" step="0.1" class="form-input" />
                <span class="unit-text">%</span>
              </div>
            </div>

            <div class="form-item">
              <label>现金 (X)</label>
              <div class="input-with-unit">
                <input v-model.number="params.cash" type="number" step="0.01" min="0" class="form-input" />
                <div class="unit-selector">
                  <button :class="{ active: params.cashUnit === 1 }" @click="params.cashUnit = 1" type="button">元</button>
                  <button :class="{ active: params.cashUnit === 100000000 }" @click="params.cashUnit = 100000000" type="button">亿</button>
                </div>
              </div>
            </div>

            <div class="form-item">
              <label>总负债 (F)</label>
              <div class="input-with-unit">
                <input v-model.number="params.debt" type="number" step="0.01" min="0" class="form-input" />
                <div class="unit-selector">
                  <button :class="{ active: params.debtUnit === 1 }" @click="params.debtUnit = 1" type="button">元</button>
                  <button :class="{ active: params.debtUnit === 100000000 }" @click="params.debtUnit = 100000000" type="button">亿</button>
                </div>
              </div>
            </div>

            <div class="form-item">
              <label>股票总数 (N)</label>
              <div class="input-with-unit">
                <input v-model.number="params.shares" type="number" step="1" min="0" class="form-input" />
                <div class="unit-selector">
                  <button :class="{ active: params.sharesUnit === 1 }" @click="params.sharesUnit = 1" type="button">股</button>
                  <button :class="{ active: params.sharesUnit === 100000000 }" @click="params.sharesUnit = 100000000" type="button">亿股</button>
                </div>
              </div>
            </div>
          </div>

          <button class="calculate-btn" @click="calculate" type="button">
            🚀 执行计算
          </button>
        </div>
      </div>

      <!-- 右侧：估值结果 -->
      <div class="results-section">
        <div class="section-title">
          <h2>💰 估值结果</h2>
        </div>

        <div class="results-grid">
          <!-- 5年估值 -->
          <div class="result-card">
            <div class="card-header">
              <h3>5年 DCF</h3>
            </div>
            <div class="card-body">
              <div class="result-row">
                <span class="result-label">每股价值</span>
                <span class="result-value large">{{ formatMoney(pricePerShare5Year) }} 元</span>
              </div>
              <div class="result-row">
                <span class="result-label">股权价值</span>
                <span class="result-value">{{ formatMoney(equityValue5Year) }}</span>
              </div>
              <div class="result-row verdict">
                <span class="result-badge" :class="isUndervalued5 ? 'undervalued' : 'overvalued'">
                  {{ isUndervalued5 ? '低估' : '高估' }} {{ Math.abs(valuationDiff5 * 100).toFixed(1) }}%
                </span>
              </div>
            </div>
          </div>

          <!-- 10年估值 -->
          <div class="result-card">
            <div class="card-header">
              <h3>10年 DCF</h3>
            </div>
            <div class="card-body">
              <div class="result-row">
                <span class="result-label">每股价值</span>
                <span class="result-value large">{{ formatMoney(pricePerShare10Year) }} 元</span>
              </div>
              <div class="result-row">
                <span class="result-label">股权价值</span>
                <span class="result-value">{{ formatMoney(equityValue10Year) }}</span>
              </div>
              <div class="result-row verdict">
                <span class="result-badge" :class="isUndervalued10 ? 'undervalued' : 'overvalued'">
                  {{ isUndervalued10 ? '低估' : '高估' }} {{ Math.abs(valuationDiff10 * 100).toFixed(1) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 对比总结 -->
        <div class="comparison-summary">
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">当前价格</span>
              <span class="summary-value">{{ formatMoney(params.currentPrice) }} 元</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">内在价值区间</span>
              <span class="summary-value range">
                {{ formatMoney(pricePerShare5Year) }} ~ {{ formatMoney(pricePerShare10Year) }} 元
              </span>
            </div>
          </div>
          <div class="final-verdict">
            <span class="verdict-badge" :class="finalVerdict === '低估' ? 'undervalued' : finalVerdict === '高估' ? 'overvalued' : 'fair'">
              {{ finalVerdict }}
            </span>
            <span class="verdict-hint">{{ finalVerdictHint }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 第二屏：现金流表格 -->
    <div class="cashflow-section">
      <div class="section-title">
        <h2>📈 未来现金流预测</h2>
      </div>
      <div class="table-container">
        <table class="cashflow-table">
          <thead>
            <tr>
              <th>年份</th>
              <th>增长率</th>
              <th>预测现金流</th>
              <th>折现系数</th>
              <th>折现现金流</th>
              <th>累计</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="year in 10" :key="year">
              <td>第 {{ year }} 年</td>
              <td>
                <span v-if="year <= 5">{{ params.growthRate }}%</span>
                <span v-else class="terminal-rate">{{ (params.growthRate / 2).toFixed(1) }}%</span>
              </td>
              <td class="money-cell">{{ formatMoney(cashflows[year - 1]) }}</td>
              <td>{{ discountFactors[year - 1]?.toFixed(4) }}</td>
              <td class="money-cell discounted">{{ formatMoney(discountedCashflows[year - 1]) }}</td>
              <td class="money-cell cumulative">{{ formatMoney(cumulativeDCF[year - 1]) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 公式说明 -->
    <div class="formula-section">
      <div class="section-title">
        <h2>📚 公式说明</h2>
      </div>
      <div class="formula-content">
        <div class="formula-card">
          <h4>现金流预测</h4>
          <p>1-5年: FCF × (1 + g)<sup>n</sup></p>
          <p>6-10年: FCF × (1 + g)<sup>5</sup> × (1 + g/2)<sup>(n-5)</sup></p>
        </div>
        <div class="formula-card">
          <h4>折现计算</h4>
          <p>折现系数 = 1 / (1 + r)<sup>n</sup></p>
        </div>
        <div class="formula-card">
          <h4>股权价值</h4>
          <p>股权价值 = EV + 现金 - 负债</p>
          <p>每股价值 = 股权价值 / 股票总数</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";

// 输入参数
const params = reactive({
  currentPrice: 150,
  fcf: 100,
  fcfUnit: 100000000,
  discountRate: 10,
  growthRate: 15,
  cash: 50,
  cashUnit: 100000000,
  debt: 30,
  debtUnit: 100000000,
  shares: 100,
  sharesUnit: 100000000,
});

// 计算结果（手动触发）
const cashflows = ref<number[]>([]);
const discountFactors = ref<number[]>([]);
const discountedCashflows = ref<number[]>([]);
const cumulativeDCF = ref<number[]>([]);
const ev5Year = ref(0);
const ev10Year = ref(0);
const equityValue5Year = ref(0);
const equityValue10Year = ref(0);
const pricePerShare5Year = ref(0);
const pricePerShare10Year = ref(0);
const isUndervalued5 = ref(true);
const valuationDiff5 = ref(0);
const isUndervalued10 = ref(true);
const valuationDiff10 = ref(0);
const finalVerdict = ref('合理');
const finalVerdictHint = ref('当前价格接近内在价值，可以考虑持有');

// 执行计算
const calculate = () => {
  const actualFCFVal = params.fcf * params.fcfUnit;
  const actualCashVal = params.cash * params.cashUnit;
  const actualDebtVal = params.debt * params.debtUnit;
  const actualSharesVal = params.shares * params.sharesUnit;

  const g = params.growthRate / 100;
  const g2 = g / 2;

  // 计算现金流
  cashflows.value = [];
  for (let year = 1; year <= 10; year++) {
    let fcfValue;
    if (year <= 5) {
      fcfValue = actualFCFVal * Math.pow(1 + g, year);
    } else {
      const fcf5 = actualFCFVal * Math.pow(1 + g, 5);
      fcfValue = fcf5 * Math.pow(1 + g2, year - 5);
    }
    cashflows.value.push(fcfValue);
  }

  // 计算折现系数
  const r = params.discountRate / 100;
  discountFactors.value = [];
  for (let year = 1; year <= 10; year++) {
    discountFactors.value.push(1 / Math.pow(1 + r, year));
  }

  // 计算折现现金流
  discountedCashflows.value = cashflows.value.map((fcf, i) => fcf * discountFactors.value[i]);

  // 计算累计折现现金流
  cumulativeDCF.value = [];
  let sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += discountedCashflows.value[i];
    cumulativeDCF.value.push(sum);
  }

  // 计算企业价值
  ev5Year.value = discountedCashflows.value.slice(0, 5).reduce((s, v) => s + v, 0);
  ev10Year.value = discountedCashflows.value.reduce((s, v) => s + v, 0);

  // 计算股权价值
  equityValue5Year.value = ev5Year.value + actualCashVal - actualDebtVal;
  equityValue10Year.value = ev10Year.value + actualCashVal - actualDebtVal;

  // 计算每股价格
  pricePerShare5Year.value = actualSharesVal === 0 ? 0 : equityValue5Year.value / actualSharesVal;
  pricePerShare10Year.value = actualSharesVal === 0 ? 0 : equityValue10Year.value / actualSharesVal;

  // 估值判断
  isUndervalued5.value = pricePerShare5Year.value > params.currentPrice;
  valuationDiff5.value = params.currentPrice === 0 ? 0 : (pricePerShare5Year.value - params.currentPrice) / params.currentPrice;
  isUndervalued10.value = pricePerShare10Year.value > params.currentPrice;
  valuationDiff10.value = params.currentPrice === 0 ? 0 : (pricePerShare10Year.value - params.currentPrice) / params.currentPrice;

  // 最终判断
  const avgPrice = (pricePerShare5Year.value + pricePerShare10Year.value) / 2;
  const diff = avgPrice - params.currentPrice;
  if (params.currentPrice === 0) {
    finalVerdict.value = '数据不足';
    finalVerdictHint.value = '请输入当前价格';
  } else {
    const ratio = diff / params.currentPrice;
    if (ratio > 0.2) {
      finalVerdict.value = '低估';
      finalVerdictHint.value = '当前价格低于内在价值，建议关注买入机会';
    } else if (ratio < -0.2) {
      finalVerdict.value = '高估';
      finalVerdictHint.value = '当前价格高于内在价值，建议谨慎或等待回调';
    } else {
      finalVerdict.value = '合理';
      finalVerdictHint.value = '当前价格接近内在价值，可以考虑持有';
    }
  }
};

// 初始化时执行一次计算
calculate();

// 格式化金额
const formatMoney = (value: number): string => {
  if (Math.abs(value) >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿';
  } else if (Math.abs(value) >= 10000) {
    return (value / 10000).toFixed(2) + '万';
  } else {
    return value.toFixed(2);
  }
};
</script>

<style scoped>
.dcf-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 15px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 主区域：左右布局 */
.main-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

@media (max-width: 900px) {
  .main-section {
    grid-template-columns: 1fr;
  }
}

.section-title {
  margin-bottom: 10px;
}

.section-title h2 {
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

/* 输入区域 */
.input-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px;
  border-radius: 8px;
}

.input-section .section-title h2 {
  color: white;
}

.input-group {
  background: white;
  padding: 15px;
  border-radius: 6px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}

.form-item label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #2c3e50;
  display: block;
  margin-bottom: 3px;
}

.input-with-unit {
  display: flex;
  gap: 5px;
}

.form-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #e1e8ed;
  border-radius: 5px;
  font-size: 13px;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.unit-text {
  padding: 6px 10px;
  background: #ecf0f1;
  border-radius: 5px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 12px;
  white-space: nowrap;
}

.unit-selector {
  display: flex;
  border: 1px solid #e1e8ed;
  border-radius: 5px;
  overflow: hidden;
}

.unit-selector button {
  padding: 6px 10px;
  border: none;
  background: #f8f9fa;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  color: #7f8c8d;
}

.unit-selector button.active {
  background: #667eea;
  color: white;
}

.calculate-btn {
  width: 100%;
  padding: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.calculate-btn:hover {
  opacity: 0.9;
}

/* 结果区域 */
.results-section {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}

.result-card {
  background: white;
  border-radius: 6px;
  padding: 12px;
}

.card-header h3 {
  font-size: 0.95rem;
  color: #667eea;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.result-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.result-label {
  font-size: 0.8rem;
  color: #7f8c8d;
}

.result-value {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.result-value.large {
  font-size: 1.1rem;
  color: #667eea;
}

.result-badge {
  padding: 3px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
}

.result-badge.undervalued {
  background: #d4edda;
  color: #155724;
}

.result-badge.overvalued {
  background: #f8d7da;
  color: #721c24;
}

.comparison-summary {
  background: white;
  border-radius: 6px;
  padding: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 10px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 0.75rem;
  color: #7f8c8d;
}

.summary-value {
  font-weight: 600;
  color: #2c3e50;
}

.summary-value.range {
  color: #667eea;
}

.final-verdict {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.verdict-badge {
  padding: 4px 12px;
  border-radius: 15px;
  font-weight: 600;
  font-size: 0.85rem;
}

.verdict-badge.undervalued { background: #d4edda; color: #155724; }
.verdict-badge.overvalued { background: #f8d7da; color: #721c24; }
.verdict-badge.fair { background: #fff3cd; color: #856404; }

.verdict-hint {
  font-size: 0.8rem;
  color: #7f8c8d;
}

/* 现金流表格 */
.cashflow-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.table-container {
  overflow-x: auto;
}

.cashflow-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.cashflow-table th,
.cashflow-table td {
  padding: 8px 10px;
  text-align: right;
  border-bottom: 1px solid #eee;
}

.cashflow-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

.cashflow-table th:first-child,
.cashflow-table td:first-child {
  text-align: left;
}

.terminal-rate {
  color: #667eea;
}

.money-cell {
  font-family: "SF Mono", Monaco, monospace;
}

.money-cell.discounted { color: #e74c3c; }
.money-cell.cumulative { color: #27ae60; font-weight: 600; }

/* 公式说明 */
.formula-section {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.formula-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.formula-card {
  background: white;
  padding: 12px;
  border-radius: 6px;
}

.formula-card h4 {
  font-size: 0.9rem;
  color: #667eea;
  margin: 0 0 8px 0;
}

.formula-card p {
  font-size: 0.8rem;
  color: #2c3e50;
  margin: 4px 0;
  font-family: "SF Mono", Monaco, monospace;
}
</style>
