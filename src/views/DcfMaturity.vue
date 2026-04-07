<template>
  <div class="dcf-maturity-container">
    <el-row :gutter="20">
      <el-col :xs="24" :md="11">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 估值参数输入区 (Valuation Parameters)</span>
              <span class="unit-hint">(金额: 亿美元 | 股本: 亿股)</span>
            </div>
          </template>

          <el-form :model="form" label-width="220px" label-position="left" size="default">

            <el-form-item>
              <template #label>
                Revenue (当前营收)
                <el-tooltip content="过去12个月(TTM)或最新财年的总营业收入" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.revenue" :min="0" :step="10" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                Operating Margin (营业利润率)
                <el-tooltip content="核心营业利润率 (EBIT Margin)，剔除非经常性损益" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.operatingMargin" :step="0.01" :precision="4" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                Tax Rate (有效税率)
                <el-tooltip content="有效税率：实际缴纳的税率，非单纯法定税率" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.taxRate" :min="0" :max="1" :step="0.01" :precision="4"
                class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                ROC (资本回报率)
                <el-tooltip content="资本回报率：成熟公司永续期ROC通常向WACC靠拢。高ROC需强护城河支撑" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.roc" :step="0.01" :precision="4" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                WACC (折现率)
                <el-tooltip content="加权平均资本成本(5%-9%)：极度敏感，0.5%误差将致估值巨变" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.wacc" :min="0.001" :step="0.005" :precision="4" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                g (永续增长率)
                <el-tooltip content="绝不可超过宏观名义GDP增速或10年期无风险国债收益率(2%-4%)" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.g" :step="0.005" :precision="4" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                Cash (现金及等价物)
                <el-tooltip content="现金、现金等价物及短期投资总额" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.cash" :min="0" :step="10" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                Total Debt (总债务)
                <el-tooltip content="含短债、长债及资本化的经营性租赁总额" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.totalDebt" :min="0" :step="10" class="full-width" />
            </el-form-item>

            <el-form-item>
              <template #label>
                Diluted Shares (摊薄总股本)
                <el-tooltip content="含潜在期权行权后的总股本，防估值虚高" placement="top">
                  <el-icon class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <el-input-number v-model="form.dilutedShares" :min="0.01" :step="1" :precision="2" class="full-width" />
            </el-form-item>

            <div class="submit-btn-wrapper">
              <el-button type="primary" size="large" @click="calculateValuation" class="full-width">
                执行 DCF 估值推导 (Run DCF)
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="13">
        <el-card class="output-card" shadow="hover" v-if="reportGenerated">
          <template #header>
            <div class="card-header">
              <span>📑 估值分析报告 (Valuation Report)</span>
            </div>
          </template>

          <div class="report-content">
            <div class="report-section">
              <h3>1. 参数回溯</h3>
              <p class="text-secondary">
                根据您提供的假设：当前营收为 <strong>{{ form.revenue }}</strong> 亿，营业利润率 <strong>{{ (form.operatingMargin *
                  100).toFixed(2)
                  }}%</strong>，有效税率 <strong>{{ (form.taxRate * 100).toFixed(2) }}%</strong>。<br />
                核心估值驱动因素中，资本回报率 (ROC) 设为 <strong>{{ (form.roc * 100).toFixed(2) }}%</strong>，折现率 (WACC) 为 <strong>{{
                  (form.wacc * 100).toFixed(2) }}%</strong>，永续增长率 (g) 限制在 <strong>{{ (form.g * 100).toFixed(2)
                  }}%</strong>。<br />
                资本结构方面，拥有现金 <strong>{{ form.cash }}</strong> 亿，总债务 <strong>{{ form.totalDebt }}</strong> 亿，摊薄总股本
                <strong>{{
                  form.dilutedShares }}</strong> 亿股。
              </p>
            </div>

            <el-divider />

            <div class="report-section">
              <h3>2. 详细推导</h3>
              <div class="step-box">
                <h4>Step 1 计算基期利润：</h4>
                <p><code>EBIT</code> = Revenue × Operating_Margin = {{ form.revenue }} × {{ form.operatingMargin }} =
                  <strong>{{ calcResults.ebit.toFixed(2) }}</strong>
                </p>
                <p><code>当前 NOPAT</code> = EBIT × (1 - Tax_Rate) = {{ calcResults.ebit.toFixed(2) }} × (1 - {{
                  form.taxRate
                  }}) = <strong>{{ calcResults.nopat.toFixed(2) }}</strong></p>
              </div>

              <div class="step-box">
                <h4>Step 2 计算再投资效率：</h4>
                <p><code>再投资率</code> = g / ROC = {{ form.g }} / {{ form.roc }} = <strong>{{
                  (calcResults.reinvestmentRate *
                    100).toFixed(2) }}%</strong></p>
              </div>

              <div class="step-box">
                <h4>Step 3 计算预期自由现金流：</h4>
                <p><code>下一年 NOPAT</code> = 当前 NOPAT × (1 + g) = {{ calcResults.nopat.toFixed(2) }} × (1 + {{ form.g }})
                  =
                  <strong>{{ calcResults.nextNopat.toFixed(2) }}</strong>
                </p>
                <p><code>FCFF1</code> = 下一年 NOPAT × (1 - 再投资率) = {{ calcResults.nextNopat.toFixed(2) }} × (1 - {{
                  calcResults.reinvestmentRate.toFixed(4) }}) = <strong>{{ calcResults.fcff1.toFixed(2) }}</strong></p>
              </div>

              <div class="step-box">
                <h4>Step 4 计算核心业务价值：</h4>
                <p><code>核心资产价值</code> = FCFF1 / (WACC - g) = {{ calcResults.fcff1.toFixed(2) }} / ({{ form.wacc }} - {{
                  form.g }}) = <strong>{{ calcResults.operatingAssetsValue.toFixed(2) }}</strong></p>
              </div>

              <div class="step-box">
                <h4>Step 5 桥接到每股价值：</h4>
                <p><code>股权总价值</code> = 核心资产价值 + Cash - Total_Debt = {{ calcResults.operatingAssetsValue.toFixed(2) }} +
                  {{
                  form.cash }} - {{ form.totalDebt }} = <strong>{{ calcResults.equityValue.toFixed(2) }}</strong></p>
                <p><code>每股内在价值</code> = 股权总价值 / Diluted_Shares = {{ calcResults.equityValue.toFixed(2) }} / {{
                  form.dilutedShares }} = <strong>{{ calcResults.valuePerShare.toFixed(2) }}</strong></p>
              </div>
            </div>

            <el-divider />

            <div class="report-section conclusion-box">
              <h3>3. 最终结论</h3>
              <div class="final-price">
                每股内在价值：<span>$ {{ calcResults.valuePerShare.toFixed(2) }}</span>
              </div>
              <div class="sensitivity-note">
                <strong>💡 敏感性提示：</strong>该估值对 <strong>WACC (折现率)</strong> 和 <strong>ROC (资本回报率)</strong> 极其敏感。当前使用的
                WACC 为 {{
                  (form.wacc * 100).toFixed(2) }}%，若实际风险偏好上升导致 WACC 上调 0.5%，估值将大幅缩水；同时，模型假设公司能在永续期维持 {{ (form.roc *
                  100).toFixed(2) }}% 的 ROC，若竞争加剧导致 ROC 向 WACC 收敛，再投资负担将加重，从而显著压低自由现金流。
              </div>
            </div>
          </div>
        </el-card>

        <el-empty v-else description="请在左侧输入参数并点击执行推导" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

const form = reactive({
  revenue: 1000,
  operatingMargin: 0.287,
  taxRate: 0.178,
  roc: 0.15,
  wacc: 0.056,
  g: 0.035,
  cash: 200,
  totalDebt: 300,
  dilutedShares: 10
})

const reportGenerated = ref(false)

const calcResults = reactive({
  ebit: 0,
  nopat: 0,
  reinvestmentRate: 0,
  nextNopat: 0,
  fcff1: 0,
  operatingAssetsValue: 0,
  equityValue: 0,
  valuePerShare: 0
})

const calculateValuation = () => {
  if (form.wacc <= form.g) {
    ElMessage.error('数学逻辑错误：WACC 必须严格大于永续增长率 (g)，否则单阶段模型失效。')
    return
  }
  if (form.roc === 0) {
    ElMessage.error('数学逻辑错误：ROC 不能为 0，否则无法计算再投资率。')
    return
  }

  // Step 1
  calcResults.ebit = form.revenue * form.operatingMargin
  calcResults.nopat = calcResults.ebit * (1 - form.taxRate)

  // Step 2
  calcResults.reinvestmentRate = form.g / form.roc

  // Step 3
  calcResults.nextNopat = calcResults.nopat * (1 + form.g)
  calcResults.fcff1 = calcResults.nextNopat * (1 - calcResults.reinvestmentRate)

  // Step 4
  calcResults.operatingAssetsValue = calcResults.fcff1 / (form.wacc - form.g)

  // Step 5
  calcResults.equityValue = calcResults.operatingAssetsValue + form.cash - form.totalDebt
  calcResults.valuePerShare = calcResults.equityValue / form.dilutedShares

  reportGenerated.value = true
  ElMessage.success('计算完成，已生成估值推导报告！')
}
</script>

<style scoped>
.dcf-maturity-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.unit-hint {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.full-width {
  width: 100%;
}

.info-icon {
  margin-left: 4px;
  color: #909399;
  cursor: help;
  vertical-align: middle;
}

.submit-btn-wrapper {
  margin-top: 30px;
}

.report-content {
  line-height: 1.6;
}

.report-section h3 {
  color: #409EFF;
  margin-bottom: 15px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.text-secondary {
  color: #606266;
  font-size: 14px;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
}

.step-box {
  background: #f4f4f5;
  padding: 12px 16px;
  margin-bottom: 10px;
  border-radius: 6px;
}

.step-box h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.step-box p {
  margin: 4px 0;
  font-family: monospace;
  font-size: 14px;
  color: #606266;
}

code {
  background-color: #e9e9eb;
  padding: 2px 6px;
  border-radius: 4px;
  color: #d32029;
}

.conclusion-box {
  background: #ecf5ff;
  padding: 20px;
  border-radius: 8px;
}

.final-price {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
}

.final-price span {
  font-size: 32px;
  color: #f56c6c;
  margin-left: 10px;
}

.sensitivity-note {
  font-size: 14px;
  color: #606266;
  border-top: 1px dashed #c6e2ff;
  padding-top: 15px;
}
</style>