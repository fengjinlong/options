<template>
  <div class="dcf-maturity-container">
    <el-row :gutter="24">
      <el-col :span="10">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 估值参数输入</span>
              <span class="unit-hint">单位: 亿美元 / 亿股</span>
            </div>
          </template>

          <div class="param-form">
            <div class="param-group">
              <div class="group-title">核心利润参数</div>
              <div class="form-row">
                <label class="form-label">
                  Revenue
                  <el-tooltip content="过去12个月(TTM)或最新财年的总营业收入" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.revenue" :min="0" :step="10" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Operating Margin
                  <el-tooltip content="核心营业利润率 (EBIT Margin)，剔除非经常性损益" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.operatingMargin" :step="0.01" :precision="4" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Tax Rate
                  <el-tooltip content="有效税率：实际缴纳的税率，非单纯法定税率" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.taxRate" :min="0" :max="1" :step="0.01" :precision="4"
                  class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">估值驱动因素</div>
              <div class="form-row">
                <label class="form-label">
                  ROC
                  <el-tooltip content="资本回报率：成熟公司永续期ROC通常向WACC靠拢" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.roc" :step="0.01" :precision="4" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  WACC
                  <el-tooltip content="加权平均资本成本(5%-9%)：极度敏感，0.5%误差将致估值巨变" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.wacc" :min="0.001" :step="0.005" :precision="4" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  g (永续增长率)
                  <el-tooltip content="绝不可超过宏观名义GDP增速或10年期无风险国债收益率(2%-4%)" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.g" :step="0.005" :precision="4" class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">资本结构</div>
              <div class="form-row">
                <label class="form-label">
                  Cash
                  <el-tooltip content="现金、现金等价物及短期投资总额" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.cash" :min="0" :step="10" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Total Debt
                  <el-tooltip content="含短债、长债及资本化的经营性租赁总额" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.totalDebt" :min="0" :step="10" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Diluted Shares
                  <el-tooltip content="含潜在期权行权后的总股本，防估值虚高" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.dilutedShares" :min="0.01" :step="1" :precision="2"
                  class="input-narrow" />
              </div>
            </div>
          </div>

          <div class="submit-btn-wrapper">
            <el-button type="primary" size="large" @click="calculateValuation" class="full-width">
              执行 DCF 估值推导
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card class="output-card" shadow="hover" v-if="reportGenerated">
          <template #header>
            <div class="card-header">
              <span>📑 估值分析报告</span>
              <div class="action-buttons">
                <el-button size="small" @click="openSaveModal" type="primary">💾 保存</el-button>
                <el-button size="small" @click="openHistoryModal" type="info">📋 记录</el-button>
              </div>
            </div>
          </template>

          <div class="report-content">
            <div class="report-section">
              <h3>1. 参数回溯</h3>
              <div class="param-summary">
                <div class="param-item">
                  <span class="param-label">当前营收</span>
                  <span class="param-value">{{ form.revenue }} 亿</span>
                </div>
                <div class="param-item">
                  <span class="param-label">营业利润率</span>
                  <span class="param-value">{{ (form.operatingMargin * 100).toFixed(2) }}%</span>
                </div>
                <div class="param-item">
                  <span class="param-label">有效税率</span>
                  <span class="param-value">{{ (form.taxRate * 100).toFixed(2) }}%</span>
                </div>
                <div class="param-item">
                  <span class="param-label">ROC</span>
                  <span class="param-value">{{ (form.roc * 100).toFixed(2) }}%</span>
                </div>
                <div class="param-item">
                  <span class="param-label">WACC</span>
                  <span class="param-value">{{ (form.wacc * 100).toFixed(2) }}%</span>
                </div>
                <div class="param-item">
                  <span class="param-label">永续增长率</span>
                  <span class="param-value">{{ (form.g * 100).toFixed(2) }}%</span>
                </div>
                <div class="param-item">
                  <span class="param-label">现金</span>
                  <span class="param-value">{{ form.cash }} 亿</span>
                </div>
                <div class="param-item">
                  <span class="param-label">总债务</span>
                  <span class="param-value">{{ form.totalDebt }} 亿</span>
                </div>
                <div class="param-item">
                  <span class="param-label">摊薄总股本</span>
                  <span class="param-value">{{ form.dilutedShares }} 亿股</span>
                </div>
              </div>
            </div>

            <el-divider />

            <div class="report-section">
              <h3>2. 详细推导</h3>
              <div class="step-grid">
                <div class="step-box">
                  <div class="step-title">Step 1 计算基期利润</div>
                  <p>EBIT = {{ form.revenue }} × {{ form.operatingMargin }} = <strong>{{ calcResults.ebit.toFixed(2)
                      }}</strong></p>
                  <p>NOPAT = {{ calcResults.ebit.toFixed(2) }} × (1 - {{ form.taxRate }}) = <strong>{{
                    calcResults.nopat.toFixed(2) }}</strong></p>
                </div>

                <div class="step-box">
                  <div class="step-title">Step 2 再投资效率</div>
                  <p>再投资率 = {{ form.g }} / {{ form.roc }} = <strong>{{ (calcResults.reinvestmentRate * 100).toFixed(2)
                      }}%</strong></p>
                </div>

                <div class="step-box">
                  <div class="step-title">Step 3 预期自由现金流</div>
                  <p>NOPAT<sub>下一年</sub> = {{ calcResults.nopat.toFixed(2) }} × (1 + {{ form.g }}) = <strong>{{
                    calcResults.nextNopat.toFixed(2) }}</strong></p>
                  <p>FCFF<sub>1</sub> = {{ calcResults.nextNopat.toFixed(2) }} × (1 - {{
                    calcResults.reinvestmentRate.toFixed(4) }}) = <strong>{{ calcResults.fcff1.toFixed(2) }}</strong>
                  </p>
                </div>

                <div class="step-box">
                  <div class="step-title">Step 4 核心业务价值</div>
                  <p>核心资产 = {{ calcResults.fcff1.toFixed(2) }} / ({{ form.wacc }} - {{ form.g }}) = <strong>{{
                    calcResults.operatingAssetsValue.toFixed(2) }}</strong></p>
                </div>

                <div class="step-box step-box-wide">
                  <div class="step-title">Step 5 每股价值</div>
                  <p>股权总价值 = {{ calcResults.operatingAssetsValue.toFixed(2) }} + {{ form.cash }} - {{ form.totalDebt }}
                    =
                    <strong>{{ calcResults.equityValue.toFixed(2) }}</strong>
                  </p>
                  <p>每股价值 = {{ calcResults.equityValue.toFixed(2) }} / {{ form.dilutedShares }} = <strong>{{
                    calcResults.valuePerShare.toFixed(2) }}</strong></p>
                </div>
              </div>
            </div>

            <el-divider />

            <div class="conclusion-box">
              <h3>3. 最终结论</h3>
              <div class="final-price">
                <span class="label">每股内在价值</span>
                <span class="value">$ {{ calcResults.valuePerShare.toFixed(2) }}</span>
              </div>
              <div class="sensitivity-note">
                <strong>💡 敏感性提示：</strong>该估值对 <strong>WACC</strong> 和 <strong>ROC</strong> 极其敏感。当前 WACC 为 {{ (form.wacc
                  *
                100).toFixed(2) }}%，若上调 0.5%，估值将大幅缩水。
              </div>
            </div>
          </div>
        </el-card>

        <el-empty v-else description="请在左侧输入参数并点击执行推导" />
      </el-col>
    </el-row>
  </div>

  <!-- 保存 Modal -->
  <div v-if="showSaveModal" class="modal-overlay" @click.self="showSaveModal = false">
    <div class="modal-box">
      <div class="modal-header">
        <h3>💾 保存估值记录</h3>
        <button class="modal-close" @click="showSaveModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div class="modal-form">
          <div class="modal-item">
            <label>标的名称</label>
            <input v-model="saveForm.name" type="text" placeholder="如：苹果公司" class="modal-input" />
          </div>
          <div class="modal-item">
            <label>日期</label>
            <input v-model="saveForm.date" type="date" class="modal-input" />
          </div>
          <div class="modal-item">
            <label>每股内在价值 ($)</label>
            <input v-model.number="saveForm.valuePerShare" type="number" step="0.01" class="modal-input" readonly />
          </div>
          <div class="modal-item">
            <label>当前价格 ($)</label>
            <input v-model.number="saveForm.currentPrice" type="number" step="0.01" class="modal-input"
              placeholder="可选" />
          </div>
        </div>
        <div class="param-preview">
          <div class="preview-title">参数预览</div>
          <div class="preview-grid">
            <span>营收: {{ form.revenue }} 亿</span>
            <span>利润率: {{ (form.operatingMargin * 100).toFixed(2) }}%</span>
            <span>税率: {{ (form.taxRate * 100).toFixed(2) }}%</span>
            <span>ROC: {{ (form.roc * 100).toFixed(2) }}%</span>
            <span>WACC: {{ (form.wacc * 100).toFixed(2) }}%</span>
            <span>g: {{ (form.g * 100).toFixed(2) }}%</span>
            <span>现金: {{ form.cash }} 亿</span>
            <span>债务: {{ form.totalDebt }} 亿</span>
            <span>股本: {{ form.dilutedShares }} 亿股</span>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="modal-btn cancel" @click="showSaveModal = false">取消</button>
        <button class="modal-btn confirm" @click="handleSave">保存</button>
      </div>
    </div>
  </div>

  <!-- 历史记录 Modal -->
  <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
    <div class="modal-box modal-history">
      <div class="modal-header">
        <h3>📋 永续 DCF 估值记录</h3>
        <button class="modal-close" @click="showHistoryModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <el-empty v-if="historyRecords.length === 0" description="暂无保存记录" />
        <el-table v-else :data="historyRecords" stripe style="width: 100%" max-height="400">
          <el-table-column prop="name" label="标的名称" width="120" center />
          <el-table-column prop="date" label="日期" width="110" />
          <el-table-column label="内在价值" width="110">
            <template #default="{ row }">
              $ {{ row.valuePerShare?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="当前价格" width="110">
            <template #default="{ row }">
              <template v-if="row.currentPrice">$ {{ row.currentPrice.toFixed(2) }}</template>
              <template v-else>-</template>
            </template>
          </el-table-column>
          <el-table-column label="折溢价" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.currentPrice" :type="getVerdictTagType(row)" size="small">
                {{ getVerdictText(row) }}
              </el-tag>
              <template v-else>-</template>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ $index }">
              <el-button size="small" type="primary" link @click="handleLoad($index)">加载</el-button>
              <el-button size="small" type="danger" link @click="handleDelete($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
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

/* ---------- 保存 / 历史记录逻辑 ---------- */
const STORAGE_KEY = 'dcf_maturity_records'

interface Record {
  id: number
  name: string
  date: string
  valuePerShare: number
  currentPrice: number | null
  params: typeof form
}

const showSaveModal = ref(false)
const showHistoryModal = ref(false)
const historyRecords = ref < Record[] > ([])

const saveForm = reactive({
  name: '',
  date: new Date().toISOString().split('T')[0],
  valuePerShare: 0,
  currentPrice: null as number | null
})

const loadRecords = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    historyRecords.value = raw ? JSON.parse(raw) : []
  } catch {
    historyRecords.value = []
  }
}

const persistRecords = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(historyRecords.value))
}

const openSaveModal = () => {
  saveForm.name = ''
  saveForm.date = new Date().toISOString().split('T')[0]
  saveForm.valuePerShare = calcResults.valuePerShare
  saveForm.currentPrice = null
  showSaveModal.value = true
}

const handleSave = () => {
  if (!saveForm.name.trim()) {
    ElMessage.warning('请输入标的名称')
    return
  }
  const record: Record = {
    id: Date.now(),
    name: saveForm.name.trim(),
    date: saveForm.date,
    valuePerShare: saveForm.valuePerShare,
    currentPrice: saveForm.currentPrice,
    params: { ...form }
  }
  historyRecords.value.unshift(record)
  persistRecords()
  showSaveModal.value = false
  ElMessage.success('记录已保存')
}

const openHistoryModal = () => {
  loadRecords()
  showHistoryModal.value = true
}

const handleLoad = (idx: number) => {
  const record = historyRecords.value[idx]
  Object.assign(form, record.params)
  calcResults.ebit = form.revenue * form.operatingMargin
  calcResults.nopat = calcResults.ebit * (1 - form.taxRate)
  calcResults.reinvestmentRate = form.g / form.roc
  calcResults.nextNopat = calcResults.nopat * (1 + form.g)
  calcResults.fcff1 = calcResults.nextNopat * (1 - calcResults.reinvestmentRate)
  calcResults.operatingAssetsValue = calcResults.fcff1 / (form.wacc - form.g)
  calcResults.equityValue = calcResults.operatingAssetsValue + form.cash - form.totalDebt
  calcResults.valuePerShare = calcResults.equityValue / form.dilutedShares
  reportGenerated.value = true
  showHistoryModal.value = false
  ElMessage.success(`已加载: ${record.name}`)
}

const handleDelete = (idx: number) => {
  historyRecords.value.splice(idx, 1)
  persistRecords()
  ElMessage.info('记录已删除')
}

const getVerdictText = (record: Record): string => {
  if (!record.currentPrice) return '-'
  const ratio = record.valuePerShare / record.currentPrice
  if (ratio > 1.2) return '低估'
  if (ratio < 0.8) return '高估'
  return '合理'
}

const getVerdictTagType = (record: Record): '' | 'success' | 'danger' | 'warning' => {
  if (!record.currentPrice) return ''
  const ratio = record.valuePerShare / record.currentPrice
  if (ratio > 1.2) return 'success'
  if (ratio < 0.8) return 'danger'
  return 'warning'
}

onMounted(() => {
  loadRecords()
})

const calculateValuation = () => {
  if (form.wacc <= form.g) {
    ElMessage.error('数学逻辑错误：WACC 必须严格大于永续���长率 (g)，否则单阶段模型失效。')
    return
  }
  if (form.roc === 0) {
    ElMessage.error('数学逻辑错误：ROC 不能为 0，否则无法计算再投资率。')
    return
  }

  calcResults.ebit = form.revenue * form.operatingMargin
  calcResults.nopat = calcResults.ebit * (1 - form.taxRate)
  calcResults.reinvestmentRate = form.g / form.roc
  calcResults.nextNopat = calcResults.nopat * (1 + form.g)
  calcResults.fcff1 = calcResults.nextNopat * (1 - calcResults.reinvestmentRate)
  calcResults.operatingAssetsValue = calcResults.fcff1 / (form.wacc - form.g)
  calcResults.equityValue = calcResults.operatingAssetsValue + form.cash - form.totalDebt
  calcResults.valuePerShare = calcResults.equityValue / form.dilutedShares

  reportGenerated.value = true
  ElMessage.success('计算完成，已生成估值推导报告！')
}
</script>

<style scoped>
.dcf-maturity-container {
  /* padding: 24px; */
  max-width: 1400px;
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

.param-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.param-group {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px 16px;
}

.group-title {
  font-weight: bold;
  font-size: 14px;
  color: #303133;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  width: 200px;
  font-size: 13px;
  color: #606266;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-narrow {
  flex: 1;
  max-width: 280px;
}

.info-icon {
  color: #909399;
  cursor: help;
}

.submit-btn-wrapper {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.full-width {
  width: 100%;
}

.report-content {
  line-height: 1.6;
}

.report-section h3 {
  color: #409EFF;
  margin-bottom: 16px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.param-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.param-item {
  background: #f8f9fa;
  padding: 10px 14px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-label {
  color: #606266;
  font-size: 13px;
}

.param-value {
  font-weight: bold;
  color: #303133;
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.step-box {
  background: #f4f4f5;
  padding: 14px 18px;
  border-radius: 8px;
}

.step-box-wide {
  grid-column: span 2;
}

.step-title {
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
  font-size: 14px;
}

.step-box p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.step-box p strong {
  color: #303133;
}

.conclusion-box {
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9eb 100%);
  padding: 24px;
  border-radius: 12px;
}

.conclusion-box h3 {
  margin-top: 0;
}

.final-price {
  background: white;
  padding: 20px 24px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.final-price .label {
  font-size: 16px;
  color: #606266;
}

.final-price .value {
  font-size: 36px;
  font-weight: bold;
  color: #f56c6c;
}

.sensitivity-note {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.sensitivity-note strong {
  color: #303133;
}

/* Modal 样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  border-radius: 10px;
  width: 480px;
  max-width: 95vw;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-history {
  width: 700px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.4rem;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 16px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.modal-item label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2c3e50;
}

.modal-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  color: #2c3e50;
}

.modal-input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-input[readonly] {
  background: #f5f7fa;
  color: #909399;
}

.param-preview {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.preview-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 20px;
  border-top: 1px solid #eee;
}

.modal-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.modal-btn.cancel {
  background: #f0f0f0;
  color: #666;
}

.modal-btn.confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
</style>