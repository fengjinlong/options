<template>
  <div class="dcf-reverse-container">
    <el-row :gutter="24">
      <el-col :xs="24" :md="10" :lg="10">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 市场与财务数据输入</span>
              <span class="unit-hint">单位: 亿美元 / 亿股</span>
            </div>
          </template>

          <div class="param-form">
            <div class="param-group">
              <div class="group-title">二级市场切片数据</div>
              <div class="form-row">
                <label class="form-label">
                  Stock Price
                  <el-tooltip content="当前二级市场股票交易价格（美元）" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.stockPrice" :min="0.01" :step="1" :precision="2" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Shares
                  <el-tooltip content="总股本（亿美元），如 10 亿股则填 10" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.shares" :min="0.01" :step="1" :precision="2" class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">资产负债表关键项</div>
              <div class="form-row">
                <label class="form-label">
                  Cash
                  <el-tooltip content="现金及现金等价物总额和短期投资" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.cash" :min="0" :step="10" :precision="2" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Total Debt
                  <el-tooltip content="含短债、长债及资本化租赁总额" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.totalDebt" :min="0" :step="10" :precision="2" class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">利润表关键项</div>
              <div class="form-row">
                <label class="form-label">
                  Operating Profit
                  <el-tooltip content="营业利润 (EBIT)，剔除非经常性损益" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.operatingProfit" :min="0" :step="5" :precision="2"
                  class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Pre-Tax Income
                  <el-tooltip content="税前利润 (EBT)" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.preTaxIncome" :min="0.01" :step="5" :precision="2"
                  class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  Income Tax
                  <el-tooltip content="实际缴纳的所得税费用数据" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.incomeTax" :step="5" :precision="2" class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">估值假设参数</div>
              <div class="form-row">
                <label class="form-label">
                  ROC
                  <el-tooltip content="资本回报率（ROC > g 时公司才能创造价值）" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.roc" :min="0.001" :step="0.01" :precision="4" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  g (永续增长率)
                  <el-tooltip content="永续增长率：不可超过名义 GDP 增速或无风险收益率（建议 2%-4%）" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.g" :min="0.001" :step="0.005" :precision="4" class="input-narrow" />
              </div>
            </div>
          </div>

          <div class="submit-btn-wrapper">
            <el-button type="primary" size="large" @click="calculateReverse" class="full-width">
              执行反向 DCF 推导
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="14" :lg="14">
        <div class="output-header">
          <span class="output-title">📑 反向 DCF 估值分析报告</span>
          <div class="action-buttons">
            <el-button size="small" @click="openSaveModal" type="primary" :disabled="!reportGenerated">💾 保存</el-button>
            <el-button size="small" @click="openHistoryModal" type="info">📋 记录</el-button>
          </div>
        </div>
        <el-card class="output-card" shadow="hover" v-if="reportGenerated">
          <div class="report-content">
            <div class="report-section">
              <h3>一、数据回溯</h3>
              <p class="intro-text">
                接收到以下公司市场切片数据与财务指标，现将其代入反向 DCF 模型，反推市场当前隐含的折现率（WACC）。
              </p>
              <div class="param-summary">
                <div class="param-item"><span class="param-label">当前股价</span><span class="param-value">$ {{
                  form.stockPrice
                    }}</span></div>
                <div class="param-item"><span class="param-label">总股本</span><span class="param-value">{{ form.shares }}
                    亿股</span></div>
                <div class="param-item"><span class="param-label">现金</span><span class="param-value">{{ form.cash }}
                    亿</span>
                </div>
                <div class="param-item"><span class="param-label">总债务</span><span class="param-value">{{ form.totalDebt
                    }}
                    亿</span></div>
                <div class="param-item"><span class="param-label">营业利润</span><span class="param-value">{{
                  form.operatingProfit
                    }} 亿</span></div>
                <div class="param-item"><span class="param-label">税前利润</span><span class="param-value">{{
                  form.preTaxIncome }}
                    亿</span></div>
                <div class="param-item"><span class="param-label">所得税费用</span><span class="param-value">{{
                  form.incomeTax }}
                    亿</span></div>
                <div class="param-item"><span class="param-label">ROC</span><span class="param-value">{{ (form.roc *
                  100).toFixed(2) }}%</span></div>
                <div class="param-item"><span class="param-label">永续增长率 (g)</span><span class="param-value">{{ (form.g *
                  100).toFixed(2) }}%</span></div>
              </div>
            </div>

            <el-divider />

            <div class="report-section">
              <h3>二、逻辑推演</h3>

              <div class="step-box">
                <div class="step-title">Step 1 — 还原核心资产标价</div>
                <p>Equity_Value = Stock_Price × Shares</p>
                <p>= {{ form.stockPrice }} × {{ form.shares }} = <strong>{{ results.equityValue.toFixed(2) }}</strong>
                </p>
                <p>Target_Core_Value = Equity_Value - Cash + Total_Debt</p>
                <p>= {{ results.equityValue.toFixed(2) }} - {{ form.cash }} + {{ form.totalDebt }} = <strong>{{
                  results.targetCoreValue.toFixed(2) }}</strong></p>
              </div>

              <div class="step-box">
                <div class="step-title">Step 2 — 计算净营业利润 <span v-if="taxSmoothed"
                    style="color:#e6a23c; font-size: 12px; margin-left:8px;">(已启用税率平滑)</span></div>
                <p>Effective_Tax_Rate = Income_Tax / Pre_Tax_Income</p>
                <p>= {{ form.incomeTax }} / {{ form.preTaxIncome }} ≈ <strong>{{ (results.effectiveTaxRate *
                  100).toFixed(2)
                    }}%</strong></p>
                <p>NOPAT = Operating_Profit × (1 - Effective_Tax_Rate)</p>
                <p>= {{ form.operatingProfit }} × (1 - {{ results.effectiveTaxRate.toFixed(4) }}) = <strong>{{
                  results.nopat.toFixed(2) }}</strong></p>
              </div>

              <div class="step-box">
                <div class="step-title">Step 3 — 推导下一年自由现金流</div>
                <p>Reinvestment_Rate = g / ROC</p>
                <p>= {{ form.g }} / {{ form.roc }} = <strong>{{ (results.reinvestmentRate * 100).toFixed(2) }}%</strong>
                </p>
                <p>Next_Year_NOPAT = NOPAT × (1 + g)</p>
                <p>= {{ results.nopat.toFixed(2) }} × (1 + {{ form.g }}) = <strong>{{ results.nextYearNopat.toFixed(2)
                    }}</strong></p>
                <p>FCFF1 = Next_Year_NOPAT × (1 - Reinvestment_Rate)</p>
                <p>= {{ results.nextYearNopat.toFixed(2) }} × (1 - {{ results.reinvestmentRate.toFixed(4) }}) =
                  <strong>{{
                    results.fcff1.toFixed(2) }}</strong>
                </p>
              </div>

              <div class="step-box step-box-highlight">
                <div class="step-title">Step 4 — 反解隐含折现率</div>
                <p>Implied_WACC = (FCFF1 / Target_Core_Value) + g</p>
                <p>= ({{ results.fcff1.toFixed(2) }} / {{ results.targetCoreValue.toFixed(2) }}) + {{ (form.g *
                  100).toFixed(2) }}%</p>
                <p class="final-result">= <strong>{{ (results.impliedWacc * 100).toFixed(2) }}%</strong></p>
              </div>
            </div>

            <el-divider />

            <div class="report-section">
              <h3>三、市场情绪判读</h3>
              <div :class="['verdict-box', verdictClass]">
                <div class="verdict-icon">{{ verdictIcon }}</div>
                <div class="verdict-content">
                  <div class="verdict-title">{{ verdictTitle }}</div>
                  <div class="verdict-desc">{{ verdictDesc }}</div>
                </div>
              </div>

              <div class="implied-wacc-compare">
                <div class="compare-item">
                  <span class="compare-label">隐含折现率 (Implied WACC)</span>
                  <span class="compare-value">{{ (results.impliedWacc * 100).toFixed(2) }}%</span>
                </div>
                <div class="compare-item">
                  <span class="compare-label">永续增长率 (g)</span>
                  <span class="compare-value">{{ (form.g * 100).toFixed(2) }}%</span>
                </div>
                <div class="compare-item">
                  <span class="compare-label">差值 (WACC - g)</span>
                  <span class="compare-value">{{ ((results.impliedWacc - form.g) * 100).toFixed(2) }}%</span>
                </div>
              </div>

              <div class="theory-note pressure-test-note" v-if="pressureTestPrice > 0">
                <strong>💡 极客级压力测试：</strong><br />
                如果您作为理性投资者，坚决要求 <strong>8.00%</strong> 的安全折现率 (WACC)，那么基于当前业务产生的自由现金流，该标的对应的合理目标股价应为 <strong>$ {{
                  pressureTestPrice.toFixed(2) }}</strong>。
                <span style="font-size: 12px; display: block; margin-top: 6px; color: #f56c6c;"
                  v-if="form.stockPrice > pressureTestPrice">
                  (当前市场价 ${{ form.stockPrice }} 远高于此标准，建议耐心等待回调)
                </span>
                <span style="font-size: 12px; display: block; margin-top: 6px; color: #67c23a;" v-else>
                  (当前市场价 ${{ form.stockPrice }} 低于此标准，存在极高的配置价值！)
                </span>
              </div>
            </div>
          </div>
        </el-card>

        <el-empty v-else class="output-empty" description="请在左侧输入市场与财务数据并点击执行推导" />
      </el-col>
    </el-row>
  </div>

  <!-- 适用性说明 -->
  <div class="applicability-section">
    <div class="applicability-header">
      <span class="applicability-title">📌 适用性说明：哪些公司适合反向 DCF 模型？</span>
    </div>
    <p class="applicability-intro">
      在投资中，选对"尺子"比量得精确更重要。反向 DCF 依赖于公司当下的现金流来推演未来，请务必确认您的评估标的符合以下分类。
    </p>

    <div class="applicability-cards">
      <div class="applicability-card card-green">
        <div class="card-badge green">🟢 最佳适用（黄金击球区）</div>
        <p><strong>特征：</strong>具备正向自由现金流、盈利极度稳定、资本开支可预测的"成熟白马股"。</p>
        <p><strong>适用行业：</strong>必选消费品（如可口可乐、沃尔玛）、公用事业与基建（如宁沪高速）、进入"养老期"的成熟科技巨头（如苹果、微软）。</p>
        <p><strong>评估效果：</strong>极佳。能精准测算出市场情绪是否存在泡沫。</p>
        <!-- 可口可乐、贵州茅台、宝洁、沃尔玛，长江电力、宁沪高速、苹果（Apple）、微软（Microsoft） -->
        <p><strong>适用公司：</strong>可口可乐、贵州茅台、宝洁、沃尔玛、长江电力、宁沪高速、苹果（Apple）、微软（Microsoft）</p>
      </div>

      <div class="applicability-card card-yellow">
        <div class="card-badge yellow">🟡 需谨慎使用（需切换多阶段模型）</div>
        <p><strong>特征：</strong>商业模式已跑通且有正向利润，但正处于高速扩张期的高成长股。</p>
        <p><strong>适用行业：</strong>成长期科技股（如英伟达、特斯拉）、高增长消费赛道。</p>
        <p><strong>评估效果：</strong>无法使用本页面的"稳定增长模型"。不能反推永续增长率，必须切换至"两阶段反向 DCF"，反推其前 5 年的超高速增长率预期。</p>
      </div>

      <div class="applicability-card card-red">
        <div class="card-badge red">🔴 绝对禁区（切勿使用本模型）</div>
        <p>遇到以下三类公司，请直接弃用 DCF 模型，否则将得出严重误导的结论：</p>
        <ol class="forbidden-list">
          <li>
            <strong>强周期股（如航运、钢铁、猪肉）：</strong>周期顶峰的暴利会导致模型错误提示"极度低估"，引诱您在最高点接盘。应改用 PB 或席勒市盈率。
          </li>
          <li>
            <strong>金融服务业（如银行、保险、券商）：</strong>金融企业的"债务"是用来生钱的原材料，无法计算纯业务自由现金流（FCFF）。应改用 PB-ROE 或股息折现模型（DDM）。
          </li>
          <li>
            <strong>早期烧钱/亏损公司（如初创 SaaS、未盈利创新药）：</strong>当前自由现金流为负数，会导致模型分母崩溃。应改用市销率（P/S）或单用户价值估算。
          </li>
        </ol>
      </div>
    </div>
  </div>

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
            <input v-model="saveForm.name" type="text" placeholder="如：可口可乐公司" class="modal-input" />
          </div>
          <div class="modal-item">
            <label>日期</label>
            <input v-model="saveForm.date" type="date" class="modal-input" />
          </div>
          <div class="modal-item">
            <label>隐含折现率</label>
            <input :value="(results.impliedWacc * 100).toFixed(2) + '%'" type="text" class="modal-input" readonly />
          </div>
          <div class="modal-item">
            <label>市场评级</label>
            <input :value="verdictTitle" type="text" class="modal-input" readonly />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="modal-btn cancel" @click="showSaveModal = false">取消</button>
        <button class="modal-btn confirm" @click="handleSave">保存</button>
      </div>
    </div>
  </div>

  <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
    <div class="modal-box modal-history">
      <div class="modal-header">
        <h3>📋 反向 DCF 估值记录</h3>
        <button class="modal-close" @click="showHistoryModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <el-empty v-if="historyRecords.length === 0" description="暂无保存记录" />
        <el-table v-else :data="historyRecords" stripe style="width: 100%" max-height="400">
          <el-table-column prop="name" label="标的名称" width="120" />
          <el-table-column prop="date" label="日期" width="110" />
          <el-table-column label="隐含 WACC" width="110">
            <template #default="{ row }">
              {{ (row.impliedWacc * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column label="市场评级" width="120">
            <template #default="{ row }">
              <el-tag :type="getVerdictTagType(row.impliedWacc, row.g)" size="small">
                {{ getVerdictLabel(row.impliedWacc, row.g) }}
              </el-tag>
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
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

// ──────────────── 表单数据 ────────────────
const form = reactive({
  stockPrice: 77,
  shares: 43,
  cash: 102.7,
  totalDebt: 455,
  operatingProfit: 137.47,
  preTaxIncome: 124.62,
  incomeTax: 22.28,
  roc: 0.15,
  g: 0.03
})

// ──────────────── 计算结果与状态 ────────────────
const results = reactive({
  equityValue: 0,
  targetCoreValue: 0,
  effectiveTaxRate: 0,
  nopat: 0,
  reinvestmentRate: 0,
  nextYearNopat: 0,
  fcff1: 0,
  impliedWacc: 0
})

const reportGenerated = ref(false)
const taxSmoothed = ref(false) // 用于标识是否触发了税率平滑保护

// ──────────────── 进阶计算属性 (压力测试) ────────────────
const pressureTestPrice = computed(() => {
  // 如果 g >= 0.08，DCF 稳定期分母无意义，返回 0
  if (form.g >= 0.08) return 0;
  const requiredWacc = 0.08;
  const targetCore = results.fcff1 / (requiredWacc - form.g);
  const targetEquity = targetCore + form.cash - form.totalDebt;
  return targetEquity > 0 ? (targetEquity / form.shares) : 0;
})

// ──────────────── 判读结果 ────────────────
const verdictIcon = computed(() => {
  const w = results.impliedWacc
  const g = form.g
  if (w <= g) return '⚠️'
  if (w < 0.055) return '🔴'
  if (w <= 0.08) return '🟡'
  return '🟢'
})

const verdictTitle = computed(() => {
  const w = results.impliedWacc
  const g = form.g
  if (w <= g) return '错误：模型失效'
  if (w < 0.055) return '高估警告'
  if (w <= 0.08) return '估值合理'
  return '低估信号'
})

const verdictDesc = computed(() => {
  const w = results.impliedWacc
  const g = form.g
  if (w <= g) return '当前股价存在极度泡沫，或增长率预设过高'
  if (w < 0.055) return '市场情绪极度狂热，隐含回报率极低，缺乏安全边际'
  if (w <= 0.08) return '市场定价处于常态区间'
  return '市场情绪悲观，要求极高的回报率，具备较高投资性价比'
})

const verdictClass = computed(() => {
  const w = results.impliedWacc
  const g = form.g
  if (w <= g) return 'verdict-error'
  if (w < 0.055) return 'verdict-danger'
  if (w <= 0.08) return 'verdict-warning'
  return 'verdict-success'
})

// ──────────────── 保存 / 历史记录 (修复类型冲突) ────────────────
const STORAGE_KEY = 'dcf_reverse_records'

// 修复点：将 Record 重命名为 ValuationRecord，避免与 TS 内置类型冲突
interface ValuationRecord {
  id: number
  name: string
  date: string
  impliedWacc: number
  g: number
  roc: number
  params: typeof form
}

const showSaveModal = ref(false)
const showHistoryModal = ref(false)
const historyRecords = ref<ValuationRecord[]>([])

const saveForm = reactive({
  name: '',
  date: new Date().toISOString().split('T')[0]
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
  showSaveModal.value = true
}

const handleSave = () => {
  if (!saveForm.name.trim()) {
    ElMessage.warning('请输入标的名称')
    return
  }
  const record: ValuationRecord = {
    id: Date.now(),
    name: saveForm.name.trim(),
    date: saveForm.date,
    impliedWacc: results.impliedWacc,
    g: form.g,
    roc: form.roc,
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
  const success = recalcResults()
  if (success) {
    reportGenerated.value = true
    showHistoryModal.value = false
    ElMessage.success(`已加载: ${record.name}`)
  }
}

const handleDelete = (idx: number) => {
  historyRecords.value.splice(idx, 1)
  persistRecords()
  ElMessage.info('记录已删除')
}

const getVerdictLabel = (wacc: number, g: number): string => {
  if (wacc <= g) return '模型失效'
  if (wacc < 0.055) return '高估警告'
  if (wacc <= 0.08) return '估值合理'
  return '低估信号'
}

const getVerdictTagType = (wacc: number, g: number): '' | 'success' | 'danger' | 'warning' | 'info' => {
  if (wacc <= g) return 'info'
  if (wacc < 0.055) return 'danger'
  if (wacc <= 0.08) return 'warning'
  return 'success'
}

// ──────────────── 核心引擎 (加入金融护栏) ────────────────
const recalcResults = (): boolean => {
  // 护栏 1：防止价值毁灭陷阱 (g 不能大于等于 ROC)
  if (form.g >= form.roc) {
    ElMessage.error('金融逻辑失效：永续增长率 (g) 绝不能大于或等于资本回报率 (ROC)！这代表公司在毁灭价值。')
    return false
  }

  // Step 1: 还原核心资产标价
  results.equityValue = form.stockPrice * form.shares
  results.targetCoreValue = results.equityValue - form.cash + form.totalDebt

  // 护栏 2：核心资产价值不能为负
  if (results.targetCoreValue <= 0) {
    ElMessage.error('计算终止：核心业务资产价值为负或零。DCF 模型不适用于此类特殊标的（如早期烧钱阶段或手持巨额现金的空壳）。')
    return false
  }

  // Step 2: 计算净营业利润 (引入税率黑洞拦截)
  let rawTaxRate = form.incomeTax / form.preTaxIncome
  if (rawTaxRate < 0 || rawTaxRate > 0.40) {
    results.effectiveTaxRate = 0.25 // 强制平滑至 25% 标准企业税率
    taxSmoothed.value = true
  } else {
    results.effectiveTaxRate = rawTaxRate
    taxSmoothed.value = false
  }

  results.nopat = form.operatingProfit * (1 - results.effectiveTaxRate)

  // Step 3: 推导下一年自由现金流
  results.reinvestmentRate = form.g / form.roc
  results.nextYearNopat = results.nopat * (1 + form.g)
  results.fcff1 = results.nextYearNopat * (1 - results.reinvestmentRate)

  // Step 4: 反解隐含折现率
  results.impliedWacc = (results.fcff1 / results.targetCoreValue) + form.g

  return true // 计算成功
}

const calculateReverse = () => {
  // 基础输入校验
  if (form.roc <= 0 || form.g < 0 || form.preTaxIncome <= 0 || form.shares <= 0 || form.stockPrice <= 0) {
    ElMessage.error('请检查输入：不能存在负数或零的异常基础数据。')
    return
  }

  // 执行带护栏的计算
  const success = recalcResults()

  if (success) {
    reportGenerated.value = true
    ElMessage.success('反向 DCF 推导完成，已生成分析报告！')
  } else {
    reportGenerated.value = false
  }
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
/* 原有的样式完全保留，这里仅添加压力测试框的样式 */
.dcf-reverse-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 右侧报告头部 */
.output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.output-title {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.output-empty {
  background: #fff;
  padding: 40px 0;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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

/* 报告区域 */
.report-content {
  line-height: 1.6;
}

.report-section h3 {
  color: #409EFF;
  margin-bottom: 16px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.intro-text {
  font-size: 14px;
  color: #606266;
  margin-bottom: 16px;
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

.step-box {
  background: #f4f4f5;
  padding: 14px 18px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.step-box-highlight {
  background: linear-gradient(135deg, #f0f9eb 0%, #ecf5ff 100%);
  border: 1px solid #67c23a;
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

.final-result {
  font-size: 20px !important;
  font-weight: bold;
  color: #67c23a !important;
  margin-top: 8px !important;
}

/* 判读区域 */
.verdict-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.verdict-error {
  background: linear-gradient(135deg, #fdf6ec 0%, #fef0e6 100%);
  border: 1px solid #e6a23c;
}

.verdict-danger {
  background: linear-gradient(135deg, #fef0f0 0%, #ffeded 100%);
  border: 1px solid #f56c6c;
}

.verdict-warning {
  background: linear-gradient(135deg, #fdf6ec 0%, #fffbf0 100%);
  border: 1px solid #e6a23c;
}

.verdict-success {
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f7e0 100%);
  border: 1px solid #67c23a;
}

.verdict-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.verdict-content {
  flex: 1;
}

.verdict-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.verdict-desc {
  font-size: 14px;
  color: #606266;
}

.implied-wacc-compare {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.compare-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #ebeef5;
}

.compare-item:last-child {
  border-bottom: none;
}

.compare-label {
  font-size: 14px;
  color: #606266;
}

.compare-value {
  font-weight: bold;
  color: #303133;
  font-size: 16px;
}

.theory-note {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 4px solid #909399;
}

.pressure-test-note {
  background: #fff8f8;
  border-left-color: #f56c6c;
  margin-top: 16px;
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

/* 适用性说明 */
.applicability-section {
  margin-top: 32px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.applicability-header {
  margin-bottom: 12px;
}

.applicability-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.applicability-intro {
  font-size: 14px;
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.8;
}

.applicability-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.applicability-card {
  background: white;
  border-radius: 10px;
  padding: 16px 20px;
  border: 1px solid #e4e7ed;
}

.card-green {
  border-left: 5px solid #67c23a;
}

.card-yellow {
  border-left: 5px solid #e6a23c;
}

.card-red {
  border-left: 5px solid #f56c6c;
}

.card-badge {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
}

.card-badge.green {
  color: #67c23a;
}

.card-badge.yellow {
  color: #e6a23c;
}

.card-badge.red {
  color: #f56c6c;
}

.applicability-card p {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  margin: 6px 0;
}

.applicability-card p:first-of-type {
  margin-top: 0;
}

.forbidden-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
  line-height: 2;
}

.forbidden-list li {
  margin-bottom: 4px;
}

.forbidden-list li strong {
  color: #303133;
}
</style>