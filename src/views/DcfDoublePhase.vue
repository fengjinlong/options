<template>
  <div class="two-stage-dcf-container">
    <div class="page-header">
      <h2>🚀 极客级：NVIDIA 两阶段反向 DCF 探测器 (精细债务版)</h2>
      <p class="subtitle">通过拆解资产负债表细项，精准还原核心资产价值，反推隐含的 5 年复合增长率。</p>
    </div>

    <el-row :gutter="24">
      <el-col :xs="24" :md="10" :lg="10">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 资产负债表与估值参数</span>
              <span class="unit-hint">单位: 亿美元 / 亿股</span>
            </div>
          </template>

          <div class="param-form">
            <div class="param-group">
              <div class="group-title">市场与股本</div>
              <div class="form-row">
                <label class="form-label">模拟当前股价 ($)</label>
                <el-input-number v-model="form.stockPrice" :min="1" :step="10" :precision="2" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">摊薄总股本 (Shares)</label>
                <el-input-number v-model="form.shares" :min="0.1" :step="1" :precision="2" class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">资产端 (Assets)</div>
              <div class="form-row">
                <label class="form-label">
                  现金及短期投资
                  <el-tooltip content="包含：现金、现金等价物、短期理财及短期国债。" placement="top">
                    <el-icon class="info-icon">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </label>
                <el-input-number v-model="form.cashAndST" :min="0" :step="10" :precision="2" class="input-narrow" />
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">负债端 (Debt Breakdown)</div>
              <div class="form-row">
                <label class="form-label">短期借款 (ST Debt)</label>
                <el-input-number v-model="form.shortTermDebt" :min="0" :step="5" :precision="2" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">长期借款 (LT Debt)</label>
                <el-input-number v-model="form.longTermDebt" :min="0" :step="10" :precision="2" class="input-narrow" />
              </div>

              <div class="net-status-bar" :class="netStatusClass">
                净债务 (Net Debt): <strong>{{ calculatedNetDebt.toFixed(2) }} 亿</strong>
                <span class="status-tag">{{ netStatusText }}</span>
              </div>
            </div>

            <div class="param-group">
              <div class="group-title">自由现金流底座 (FCF)</div>
              <div class="form-row">
                <label class="form-label">基期自由现金流 (Year 0)</label>
                <el-input-number v-model="form.fcf0" :min="1" :step="10" :precision="2" class="input-narrow" />
              </div>
            </div>

            <div class="param-group param-group-highlight">
              <div class="group-title">🔒 估值锚点</div>
              <div class="form-row">
                <label class="form-label">要求回报率 (WACC)</label>
                <el-input-number v-model="form.wacc" :min="0.05" :step="0.005" :precision="4" class="input-narrow" />
              </div>
              <div class="form-row">
                <label class="form-label">永续增长率 (g_term)</label>
                <el-input-number v-model="form.gTerm" :min="0.01" :max="form.wacc - 0.01" :step="0.005" :precision="4"
                  class="input-narrow" />
              </div>
            </div>
          </div>

          <div class="submit-btn-wrapper">
            <el-button type="primary" size="large" @click="solveImpliedGrowth" class="full-width"
              :loading="isCalculating">
              🚀 反解隐含 CAGR
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="14" :lg="14">
        <div class="output-header">
          <span class="output-title">🎯 预期解剖报告</span>
          <div class="action-buttons">
            <el-button size="small" @click="openSaveModal" type="primary" :disabled="!reportGenerated">💾 保存</el-button>
            <el-button size="small" @click="openHistoryModal" type="info">📋 记录</el-button>
          </div>
        </div>
        <el-card class="output-card" shadow="hover" v-if="reportGenerated">

          <div class="report-content">
            <div class="result-hero-box">
              <div class="hero-label">当前股价隐含的未来 5 年复合增长率要求：</div>
              <div class="hero-value" :class="sentimentClass">{{ (results.impliedCagr * 100).toFixed(2) }}%</div>
            </div>

            <div class="report-section">
              <h3>一、 市场情绪判定</h3>
              <div :class="['verdict-box', sentimentClass]">
                <div class="verdict-icon">{{ sentimentIcon }}</div>
                <div class="verdict-content">
                  <div class="verdict-title">{{ sentimentTitle }}</div>
                  <div class="verdict-desc">{{ sentimentDesc }}</div>
                </div>
              </div>
            </div>

            <div class="report-section pressure-test-section">
              <h3>二、 商业现实碰撞 (TAM 测试)</h3>
              <p class="intro-text">
                年化 <strong>{{ (results.impliedCagr * 100).toFixed(2) }}%</strong> 的复利意味着：
              </p>

              <div class="reality-check-grid">
                <div class="check-card">
                  <div class="check-label">Year 0 FCF</div>
                  <div class="check-value">{{ form.fcf0.toFixed(2) }} <span class="unit">亿</span></div>
                </div>
                <div class="check-card arrow-card">
                  <el-icon :size="24">
                    <Right />
                  </el-icon>
                  <div class="mutiplier-text">{{ Math.pow(1 + results.impliedCagr, 5).toFixed(2) }}x</div>
                </div>
                <div class="check-card highlight-card">
                  <div class="check-label">Year 5 目标 FCF</div>
                  <div class="check-value danger-text">{{ results.year5Fcf.toFixed(2) }} <span class="unit">亿</span>
                  </div>
                </div>
              </div>

              <div class="theory-note">
                <strong>💡 灵魂拷问：</strong><br />
                五年后英伟达每年需产生 <strong>{{ results.year5Fcf.toFixed(0) }} 亿</strong> 现金流。若净利率按 40% 计算，年营收需达 <strong>{{
                  (results.year5Fcf / 0.4).toFixed(0) }} 亿</strong>。请评估 AI 算力总盘子是否装得下这个巨无霸。
              </div>
            </div>

            <div class="report-section">
              <h3>三、 极客解析：计算逻辑</h3>
              <el-collapse v-model="activeCollapse">
                <el-collapse-item title="查看计算明细" name="1">
                  <div class="math-box">
                    <ul class="step-list">
                      <li>
                        <strong>1. 债务汇总：</strong><br />
                        短期 ({{ form.shortTermDebt }}) + 长期 ({{ form.longTermDebt }}) = {{ (form.shortTermDebt +
                          form.longTermDebt).toFixed(2) }} 亿
                      </li>
                      <li>
                        <strong>2. 净债务结算：</strong><br />
                        总债务 - 广义现金 ({{ form.cashAndST }}) = <strong>{{ calculatedNetDebt.toFixed(2) }} 亿</strong>
                      </li>
                      <li>
                        <strong>3. 核心资产价值 (EV)：</strong><br />
                        市值 ({{ (form.stockPrice * form.shares).toFixed(2) }}) + 净债务 = <strong>{{
                          results.targetCoreValue.toFixed(2) }} 亿</strong>
                      </li>
                      <li>
                        <strong>4. 求解完成：</strong><br />
                        经过 {{ results.iterations }} 次二分迭代，找到最接近 EV 的 $g_{short}$。
                      </li>
                    </ul>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </el-card>

        <el-empty v-else class="output-empty" description="请输入数据并启动引擎" />
      </el-col>
    </el-row>

    <!-- 模型适用说明 -->
    <div class="model-guide">
      <h3>🟢 完美击球区（最适用）</h3>
      <p>这类公司满足所有使用条件：<strong>有正向现金流、增速远超宏观经济、具备极深的护城河（能跨越周期成为收割者）</strong>。用这套模型给它们做压力测试，效果极佳。</p>

      <ul>
        <li><strong>AI 算力产业链（The Pick-and-Shovel Plays）：</strong>如英伟达 (NVDA)、AMD、博通 (AVGO)、台积电 (TSM)。由于处于风口，它们的短期增速极高，但由于半导体的周期属性，远期一定会回落，完美契合"高成长 → 稳态永续"的两阶段逻辑。</li>
        <li><strong>跨越奇点的新能源/智驾寡头（The EV Leaders）：</strong>如特斯拉 (TSLA)、宁德时代 (CATL)。它们已度过疯狂烧钱期，开始产生巨额自由现金流，但市场对其未来 5 年的增速分歧极大（例如特斯拉到底是车企还是 AI 企业）。</li>
        <li><strong>具备第二曲线的互联网巨头（The Platform Monopolies）：</strong>如 Meta（AI 赋能广告）、拼多多 (PDD)（Temu 跨境出海）。主营业务提供充沛的基期现金流，新业务提供高成长预期。</li>
        <li><strong>高壁垒创新药/医疗器械寡头（The Healthcare Innovators）：</strong>如直觉外科 (ISRG)（手术机器人）、诺和诺德 (NVO) / 礼来 (LLY)（减肥药双雄）。在专利保护期内，它们能享受爆发式的利润增长。</li>
      </ul>

      <h3>🔴 绝对禁区（不可使用）</h3>
      <p>遇到以下三类公司，请<strong>直接弃用本模型</strong>。如果强行套用，算出的隐含增速（CAGR）将毫无意义：</p>

      <ol>
        <li><strong>初创期/烧钱换增长的公司（如未盈利的 SaaS、Biotech）：</strong>自由现金流 (FCF) 为负数。数学公式无法对负数进行复合增长折现。应改用市销率 (P/S)、单用户价值或期权估值法。</li>
        <li><strong>金融企业（银行、保险、券商）：</strong>它们的"债务"就是原材料，无法清晰界定"净债务"和纯粹的"自由现金流"。应改用股息折现模型 (DDM) 或 PB-ROE 模型。</li>
        <li><strong>强周期性大宗商品（航运、煤炭、钢铁）：</strong>利润波动极其剧烈。用周期顶峰的暴利作为"基期现金流"去推演未来，会导致模型严重失真，错把周期顶部的估值陷阱当成便宜货。应改用席勒市盈率 (CAPE) 或市净率 (PB)。</li>
      </ol>
    </div>
  </div>

  <!-- 保存记录模态框 -->
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
            <input v-model="saveForm.name" type="text" placeholder="如：NVIDIA 两阶段 DCF" class="modal-input" />
          </div>
          <div class="modal-item">
            <label>日期</label>
            <input v-model="saveForm.date" type="date" class="modal-input" />
          </div>
          <div class="modal-item">
            <label>隐含 CAGR</label>
            <input :value="(results.impliedCagr * 100).toFixed(2) + '%'" type="text" class="modal-input" readonly />
          </div>
          <div class="modal-item">
            <label>市场情绪</label>
            <input :value="sentimentTitle" type="text" class="modal-input" readonly />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="modal-btn cancel" @click="showSaveModal = false">取消</button>
        <button class="modal-btn confirm" @click="handleSave">保存</button>
      </div>
    </div>
  </div>

  <!-- 历史记录模态框 -->
  <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
    <div class="modal-box modal-history">
      <div class="modal-header">
        <h3>📋 两阶段 DCF 估值记录</h3>
        <button class="modal-close" @click="showHistoryModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <el-empty v-if="historyRecords.length === 0" description="暂无保存记录" />
        <el-table v-else :data="historyRecords" stripe style="width: 100%" max-height="400">
          <el-table-column prop="name" label="标的名称" min-width="140" />
          <el-table-column prop="date" label="日期" min-width="100" />
          <el-table-column prop="params.stockPrice" label="股价" min-width="80">
            <template #default="{ row }">
              ${{ row.params.stockPrice }}
            </template>
          </el-table-column>
          <el-table-column label="隐含 CAGR" min-width="100">
            <template #default="{ row }">
              {{ (row.impliedCagr * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column label="市场情绪" min-width="120">
            <template #default="{ row }">
              <el-tag :type="getSentimentTagType(row.impliedCagr)" size="small">
                {{ getSentimentLabel(row.impliedCagr) }}
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
import { InfoFilled, Right } from '@element-plus/icons-vue'

// ==========================================
// 1. 响应式数据状态 (默认填充 NVIDIA 近似参数)
// ==========================================
const form = reactive({
  stockPrice: 184,
  shares: 243,
  fcf0: 966.76,          // 基期自由现金流 (Year 0)
  cashAndST: 625.56,     // 广义现金总额 (现金和现金等价物和短期投资)
  shortTermDebt: 10,  // 一年内到期的债务
  longTermDebt: 74.69,  // 长期负债
  wacc: 0.09,         // 加权平均资本成本 (投资者要求的年化收益率)
  gTerm: 0.03         // 永续增长率 (第 6 年及以后的龟速增长，绝不可超过 GDP 增速)
})

// 存储算法结算后的结果
const results = reactive({
  targetCoreValue: 0, // 核心资产目标价值 (Enterprise Value)
  impliedCagr: 0,     // 算出的前五年隐含复合增长率
  year5Fcf: 0,        // 第五年必须达到的自由现金流金额
  iterations: 0       // 二分查找循环次数
})

// UI 渲染控制开关
const reportGenerated = ref(false)
const isCalculating = ref(false)
const activeCollapse = ref(['1'])

// ==========================================
// 2. 财务逻辑自动计算属性 (Computed)
// ==========================================

/**
 * 净债务 (Net Debt) = (短期借款 + 长期借款) - 广义现金
 * 如果得数为负数，说明公司的现金储备大于总负债，处于非常健康的“净现金”状态。
 */
const calculatedNetDebt = computed(() => {
  return (form.shortTermDebt + form.longTermDebt) - form.cashAndST
})

// 基于净债务正负号的动态 UI 样式判定
const netStatusText = computed(() => calculatedNetDebt.value < 0 ? '净现金' : '净负债')
const netStatusClass = computed(() => calculatedNetDebt.value < 0 ? 'status-safe' : 'status-warn')

// ==========================================
// 3. 核心算法引擎：利用二分查找法反解隐含 CAGR
// ==========================================
const solveImpliedGrowth = () => {
  // --- 边界与常识校验 ---
  if (form.wacc <= form.gTerm) {
    ElMessage.error('WACC 必须严格大于永续增长率 (g_term)！否则公式分母为负，企业价值将无穷大。');
    return
  }
  if (form.fcf0 <= 0) {
    ElMessage.error('模型不适用！基期自由现金流必须为正。若评估亏损企业，请切换至市销率(P/S)或研发重述模型。');
    return
  }

  isCalculating.value = true

  // 第一步：计算目标企业价值 (Enterprise Value, 简称 EV)
  // 逻辑：EV = 市值 + 净债务。这是市场给公司主营业务开出的“净买单价”。
  const targetCoreValue = (form.stockPrice * form.shares) + calculatedNetDebt.value
  results.targetCoreValue = targetCoreValue

  // 第二步：初始化二分查找环境
  let low = -0.5       // 极度悲观下界：假设未来五年每年萎缩 50%
  let high = 3.0       // 极度乐观上界：假设未来五年每年暴涨 300%
  let mid = 0          // 游标：当前猜测的复合增长率
  let iterations = 0

  // 开始循环夹击求解 (设定最高 100 次以防性能卡死)
  while (low <= high && iterations < 100) {
    iterations++
    mid = (low + high) / 2 // 每次取中间值进行测试

    // 调用两阶段折现公式，计算在这个猜测的增速下，公司值多少钱
    let val = calculateTwoStageValue(mid, form.wacc, form.gTerm, form.fcf0)

    // 如果算出的价值与实际市场 EV 差距在 0.5 亿美元以内，认为算法成功收敛
    if (Math.abs(val - targetCoreValue) <= 0.5) break

    // 根据差值方向，动态调整游标上下界
    if (val > targetCoreValue) {
      high = mid // 算出来的估值太高了，说明我们猜测的增速太乐观，必须把上界压低
    } else {
      low = mid  // 算出来的估值太低了，必须把下界提上去
    }
  }

  // 第三步：存储有效结果，准备渲染报告
  results.impliedCagr = mid
  results.iterations = iterations
  // 使用复利公式计算第 5 年的终点现金流：FCF_5 = FCF_0 * (1 + CAGR)^5
  results.year5Fcf = form.fcf0 * Math.pow(1 + mid, 5)

  // 稍微延迟 300ms 结束 Loading 状态，增强专业软件的运算体感
  setTimeout(() => {
    isCalculating.value = false;
    reportGenerated.value = true
  }, 300)
}

/**
 * 辅助算法：两阶段自由现金流折现 (Two-Stage DCF) 现值计算器
 * @param cagr - 第一阶段（前 5 年）的超高速复合增长率
 * @param wacc - 加权平均资本成本（折现率）
 * @param gTerm - 第二阶段（第 6 年及以后）的永续龟速增长率
 * @param fcf0 - 基期起点自由现金流
 * @returns 折现回 Year 0 的总企业现值 (PV)
 */
const calculateTwoStageValue = (cagr: number, wacc: number, gTerm: number, fcf0: number): number => {
  let pv = 0
  let curFcf = fcf0

  // 【阶段一：高成长折现】
  // 逐年计算前 5 年的现金流，并分别折现回今天
  for (let t = 1; t <= 5; t++) {
    curFcf *= (1 + cagr) // 当前年份的现金流金额
    pv += curFcf / Math.pow(1 + wacc, t) // 折现公式：CF / (1 + r)^n
  }

  // 【阶段二：永续终值计算与折现】
  // 此时 curFcf 已经是第 5 年末的金额 (FCF_5)。
  // 使用戈登增长模型 (Gordon Growth Model) 计算从第 6 年到永远的总价值（这笔巨款站在第 5 年的时点上）：
  // TV_5 = (FCF_5 * (1 + 永续增长率)) / (折现率 - 永续增长率)
  const terminalValue = (curFcf * (1 + gTerm)) / (wacc - gTerm)

  // 将这笔在第 5 年的巨款，再统一折现 5 年回到今天
  const pvTerminalValue = terminalValue / Math.pow(1 + wacc, 5)

  // 返回总价值
  return pv + pvTerminalValue
}

// ==========================================
// 4. 情绪定性字典 (标准化 ifelse 处理)
// 统一管控文本、样式类名和图标
// ==========================================

const sentimentClass = computed(() => {
  if (results.impliedCagr > 0.4) return 'verdict-danger'
  if (results.impliedCagr >= 0.25) return 'verdict-warning'
  return 'verdict-success'
})

const sentimentIcon = computed(() => {
  if (results.impliedCagr > 0.4) return '🔥'
  if (results.impliedCagr >= 0.25) return '⚔️'
  return '💎'
})

const sentimentTitle = computed(() => {
  if (results.impliedCagr > 0.4) return '预期极度苛刻'
  if (results.impliedCagr >= 0.25) return '预期合理/饱满'
  return '预期悲观'
})

const sentimentDesc = computed(() => {
  if (results.impliedCagr > 0.4) return '市场要求极高增速，容错率极低。这通常标志着周期见顶或严重泡沫。'
  if (results.impliedCagr >= 0.25) return '定价完全反映了行业龙头的正常扩张红利。买入需密切关注后续季报是否爆雷。'
  return '市场低估了成长潜力。若你确信行业仍在爆发期，这是绝佳的左侧买入击球区。'
})

// ──────────────── 保存 / 历史记录 ────────────────
const STORAGE_KEY = 'dcf_double_phase_records'

// 估值记录数据结构
interface ValuationRecord {
  id: number
  name: string
  date: string
  impliedCagr: number
  wacc: number
  gTerm: number
  params: typeof form
}

const showSaveModal = ref(false)
const showHistoryModal = ref(false)
const historyRecords = ref<ValuationRecord[]>([])

const saveForm = reactive({
  name: '',
  date: new Date().toISOString().split('T')[0]
})

// 从 localStorage 加载历史记录
const loadRecords = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    historyRecords.value = raw ? JSON.parse(raw) : []
  } catch {
    historyRecords.value = []
  }
}

// 持久化历史记录到 localStorage
const persistRecords = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(historyRecords.value))
}

// 打开保存模态框
const openSaveModal = () => {
  saveForm.name = ''
  saveForm.date = new Date().toISOString().split('T')[0]
  showSaveModal.value = true
}

// 执行保存操作
const handleSave = () => {
  if (!saveForm.name.trim()) {
    ElMessage.warning('请输入标的名称')
    return
  }
  const record: ValuationRecord = {
    id: Date.now(),
    name: saveForm.name.trim(),
    date: saveForm.date,
    impliedCagr: results.impliedCagr,
    wacc: form.wacc,
    gTerm: form.gTerm,
    params: { ...form }
  }
  historyRecords.value.unshift(record)
  persistRecords()
  showSaveModal.value = false
  ElMessage.success('记录已保存')
}

// 打开历史记录模态框
const openHistoryModal = () => {
  loadRecords()
  showHistoryModal.value = true
}

// 从历史记录加载参数并重新计算
const handleLoad = (idx: number) => {
  const record = historyRecords.value[idx]
  Object.assign(form, record.params)
  // 重新执行计算逻辑
  solveImpliedGrowth()
  showHistoryModal.value = false
  ElMessage.success(`已加载: ${record.name}`)
}

// 删除历史记录
const handleDelete = (idx: number) => {
  historyRecords.value.splice(idx, 1)
  persistRecords()
  ElMessage.info('记录已删除')
}

// 根据隐含 CAGR 获取情绪标签文本
const getSentimentLabel = (cagr: number): string => {
  if (cagr > 0.4) return '预期极度苛刻'
  if (cagr >= 0.25) return '预期合理/饱满'
  return '预期悲观'
}

// 根据隐含 CAGR 获取情绪标签类型
const getSentimentTagType = (cagr: number): '' | 'success' | 'danger' | 'warning' => {
  if (cagr > 0.4) return 'danger'
  if (cagr >= 0.25) return 'warning'
  return 'success'
}

// 页面加载时读取历史记录
onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
/* 最外层容器约束 */
.two-stage-dcf-container {
  max-width: 1300px;
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

.page-header {
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

/* 左侧输入表单群组样式 */
.param-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 15px;
}

.group-title {
  font-weight: bold;
  margin-bottom: 10px;
  font-size: 14px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.form-label {
  width: 180px;
  font-size: 13px;
  color: #666;
}

.input-narrow {
  flex: 1;
  max-width: 200px;
}

/* 净债务动态状态条 */
.net-status-bar {
  margin-top: 10px;
  font-size: 12px;
  padding: 6px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-safe {
  background: #f0f9eb;
  color: #67c23a;
  border: 1px solid #e1f3d8;
}

.status-warn {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fde2e2;
}

/* 右侧分析报告 - 核心大字报 */
.result-hero-box {
  text-align: center;
  background: #fdfdfd;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #eee;
  margin-bottom: 20px;
}

.hero-value {
  font-size: 48px;
  font-weight: bold;
}

/* 定性分析框样式 */
.verdict-box {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.verdict-danger {
  background: #fef0f0;
  border: 1px solid #f56c6c;
  color: #f56c6c;
}

.verdict-warning {
  background: #fdf6ec;
  border: 1px solid #e6a23c;
  color: #e6a23c;
}

.verdict-success {
  background: #f0f9eb;
  border: 1px solid #67c23a;
  color: #67c23a;
}

/* 压力测试碰撞网格 */
.reality-check-grid {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.check-card {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  flex: 1;
  text-align: center;
  border: 1px solid #eee;
}

.highlight-card {
  background: #fff5f5;
  border-color: #ffcccc;
}

/* 算法解析黑板风格 */
.math-box {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
}

.step-list {
  list-style: none;
  padding: 0;
}

.step-list strong {
  color: #409EFF;
}

/* 模态框样式 */
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
  width: 900px;
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

/* 模型适用说明 */
.model-guide {
  margin-top: 40px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  max-width: 1300px;
  margin-left: auto;
  margin-right: auto;
}

.model-guide h3 {
  margin-top: 20px;
  margin-bottom: 12px;
  font-size: 1.1rem;
  color: #2c3e50;
}

.model-guide h3:first-child {
  margin-top: 0;
}

.model-guide p {
  line-height: 1.8;
  color: #495057;
  margin-bottom: 12px;
}

.model-guide ul,
.model-guide ol {
  margin-left: 24px;
  margin-bottom: 16px;
}

.model-guide li {
  line-height: 1.8;
  color: #495057;
  margin-bottom: 8px;
}
</style>
