<template>
  <div :class="['audit-container', form.side ? `theme-${form.side}` : 'theme-neutral']">
    <el-card class="box-card master-card" v-loading="isFetchingData">
      <template #header>
        <div class="card-header">
          <span class="title">期权六维流水线审计引擎 (V2.2) - 盘口BP自动解析版</span>
          <div class="header-tags">
            <el-tag :type="form.side === 'buyer' ? 'primary' : (form.side === 'seller' ? 'warning' : 'info')"
              effect="dark">
              当前路径: {{ form.side === 'buyer' ? '买方 (Long)' : (form.side === 'seller' ? '卖方 (Short)' : '待定 (评估中)') }}
            </el-tag>
            <el-tag type="success">实时 API 接入</el-tag>
          </div>
        </div>
      </template>

      <div class="global-control-panel">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择到期日">
              <el-select v-model="selectedDate" @change="fetchOptionsData" placeholder="正在加载..." class="w-full">
                <el-option v-for="date in availableDates" :key="date" :label="date" :value="date" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="选择合约">
              <el-select v-model="selectedContract" @change="fillContractData" :loading="isLoadingContracts"
                class="w-full">
                <el-option v-for="opt in currentOptions" :key="opt.instrument_name" :label="opt.instrument_name"
                  :value="opt.instrument_name" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="micro-text" style="text-align: right; color: #909399;">
          剩余天数 (DTE): <el-tag size="small" type="info">{{ form.dte !== null ? form.dte + ' 天' : '--' }}</el-tag>
        </div>
      </div>

      <el-alert v-if="diagnosticMode" title="⚠️ 系统检测到高危风险指标" type="error"
        description="某项指标已触发极性熔断阈值。系统已解除硬锁定，您可以继续执行后续模块进行全链条压力测试。" show-icon effect="dark" class="meltdown-alert" />

      <el-collapse v-model="activeModules" class="pipeline-collapse">

        <el-collapse-item name="m1" class="module-block">
          <template #title>
            <div class="module-title"><span class="step-num">M1</span> 全维度 IV 计分审计表 (双轨评估) <div
                :class="['status-light', m1State.done ? 'bg-green' : 'bg-gray']"></div>
            </div>
          </template>
          <div class="module-content">
            <el-row :gutter="20">
              <el-col :span="6"><el-input v-model="form.iv"><template #prepend>当前 IV</template></el-input></el-col>
              <el-col :span="6"><el-input v-model="form.rv"><template #prepend>历史 RV</template></el-input></el-col>
              <el-col :span="6"><el-input v-model="form.ivp"><template #prepend>IV 分位</template></el-input></el-col>
              <el-col :span="6">
                <el-select v-model="form.termStructure" placeholder="期限结构">
                  <el-option label="近月 < 远月 (升水 Contango)" value="contango" />
                  <el-option label="近月 > 远月 (贴水 Backwardation)" value="backwardation" />
                </el-select>
              </el-col>
            </el-row>
            <el-row :gutter="20" class="mt-15">
              <el-col :span="6">
                <el-input v-model="form.iv25dPut" placeholder="手动填入">
                  <template #prepend>25D Put IV</template>
                </el-input>
              </el-col>
              <el-col :span="6">
                <el-input v-model="form.iv25dCall" placeholder="手动填入">
                  <template #prepend>25D Call IV</template>
                </el-input>
              </el-col>
            </el-row>

            <el-button type="primary" class="mt-15 w-full" @click="auditM1" size="large">执行 M1 双轨并发评估</el-button>

            <div v-if="m1State.done" class="audit-result mt-20">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="role-card seller-card">
                    <h4>📉 卖方评估面板 (Short)</h4>
                    <p class="score-display">综合得分: <strong>{{ m1State.seller.score }}</strong> 分 (<span
                        :class="m1State.seller.score >= 25 ? 'text-green' : 'text-red'">{{ m1State.seller.desc
                        }}</span>)</p>
                    <div class="trace-log">
                      <div class="trace-line" v-for="(line, idx) in m1State.seller.trace" :key="idx">> {{ line }}</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="role-card buyer-card">
                    <h4>📈 买方评估面板 (Long)</h4>
                    <p class="score-display">综合得分: <strong>{{ m1State.buyer.score }}</strong> 分 (<span
                        :class="m1State.buyer.score >= 30 ? 'text-green' : 'text-red'">{{ m1State.buyer.desc }}</span>)
                    </p>
                    <div class="trace-log">
                      <div class="trace-line" v-for="(line, idx) in m1State.buyer.trace" :key="idx">> {{ line }}</div>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <div class="role-selector mt-20 center">
                <h4 class="mb-15" style="color: #606266;">👇 基于以上双轨诊断数据，请选择您要推演的交易路径：</h4>
                <el-radio-group v-model="form.side" size="large">
                  <el-radio-button label="seller">锁定为 卖方(Short) 推进后续模块</el-radio-button>
                  <el-radio-button label="buyer">锁定为 买方(Long) 推进后续模块</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item name="m2" class="module-block">
          <template #title>
            <div class="module-title"><span class="step-num">M2</span> 策略选型决策树 <div
                :class="['status-light', 'bg-' + m2State.status]"></div>
            </div>
          </template>
          <div class="module-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-select v-model="form.confidence" placeholder="主观信心强度 (权重40)" class="w-full">
                  <el-option label="极强 (40分)" value="40" />
                  <el-option label="中等 (20分)" value="20" />
                  <el-option label="试探性 (10分)" value="10" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-select v-model="form.targetSpace" placeholder="目标空间 (权重30)" class="w-full">
                  <el-option label="无阻力 (30分)" value="30" />
                  <el-option label="阶梯阻力 (10分)" value="10" />
                  <el-option label="震荡 (0分)" value="0" />
                </el-select>
              </el-col>
            </el-row>
            <el-button type="primary" class="mt-15" @click="auditM2">执行 M2 审计</el-button>

            <div v-if="m2State.done" class="audit-result mt-15">
              <el-tag type="warning" effect="dark" size="large">{{ m2State.strategy }} ({{ m2State.score }} 分)</el-tag>
              <div class="trace-log mt-10">
                <div class="trace-title">🔍 M2 权重打分与策略推导:</div>
                <div v-for="(line, idx) in m2State.trace" :key="idx" class="trace-line">> {{ line }}</div>
              </div>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item name="m3" class="module-block">
          <template #title>
            <div class="module-title"><span class="step-num">M3</span> 流动性三维审计 <div
                :class="['status-light', 'bg-' + m3State.status]"></div>
            </div>
          </template>
          <div class="module-content">
            <el-row :gutter="15">
              <el-col :span="8"><el-input v-model="form.spreadBp" placeholder="API自动填入"><template
                    #prepend>价差(BP)</template></el-input></el-col>
              <el-col :span="8"><el-input v-model="form.depthRatio" placeholder="需手动输入"><template
                    #prepend>挂单/计划比</template></el-input></el-col>
            </el-row>
            <el-button type="primary" class="mt-15" @click="auditM3">执行 M3 审计</el-button>

            <div v-if="m3State.done" class="audit-result mt-15">
              <p>得分: <strong>{{ m3State.score }} 分</strong> ({{ m3State.action }})</p>
              <div class="trace-log">
                <div class="trace-title">🔍 M3 摩擦成本与承载力结算:</div>
                <div v-for="(line, idx) in m3State.trace" :key="idx" class="trace-line">> {{ line }}</div>
              </div>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item name="m4" class="module-block">
          <template #title>
            <div class="module-title"><span class="step-num">M4</span> 希腊字母风控引擎 <div
                :class="['status-light', 'bg-' + m4State.status]"></div>
            </div>
          </template>
          <div class="module-content">
            <el-row :gutter="10">
              <el-col :span="6"><el-input v-model="form.delta"><template #prepend>Delta</template></el-input></el-col>
              <el-col :span="6"><el-input v-model="form.gamma"><template #prepend>Gamma</template></el-input></el-col>
              <el-col :span="6"><el-input v-model="form.theta"><template #prepend>Theta</template></el-input></el-col>
            </el-row>
            <el-button type="primary" class="mt-15" @click="auditM4">执行 M4 审计</el-button>

            <div v-if="m4State.done" class="audit-result mt-15">
              <div class="trace-log mb-10">
                <div class="trace-title">🔍 M4 极端参数代入公式验证:</div>
                <div v-for="(line, idx) in m4State.trace" :key="idx" class="trace-line">> {{ line }}</div>
              </div>
              <div v-for="res in m4State.constraints" :key="res.name"
                :class="['constraint-line', res.pass ? 'text-green' : 'text-red']">
                {{ res.pass ? '✅' : '❌' }} {{ res.name }}: {{ res.desc }}
              </div>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item name="m6" class="module-block final-block">
          <template #title>
            <div class="module-title"><span class="step-num">M6</span> 动态汇总决策中心</div>
          </template>
          <div class="module-content center">
            <el-button type="success" size="large" @click="generateFinalDecision"
              style="width: 50%; font-weight: bold;">汇总统分并生成决策方案</el-button>

            <div v-if="finalDecision" class="decision-board mt-20">
              <h2>综合评分: <span class="score-huge">{{ finalScore }}</span></h2>
              <el-tag effect="dark" size="large" :type="finalActionType">{{ finalActionText }}</el-tag>

              <div class="trace-log mt-15" style="text-align: left;">
                <div class="trace-title">⚖️ M6 加权统分逻辑:</div>
                <div class="trace-line">> 基准角色 = {{ form.side === 'seller' ? '卖方 (Short)' : '买方 (Long)' }}</div>
                <div class="trace-line">> 公式 = (M1当前角色得分 × 3) + (M2 × 0.25) + (M3 × 2) + (M4 × 0.15)</div>
                <div class="trace-line">> 代入 = ({{ currentM1Score }} × 3) + ({{ m2State.score }} × 0.25) +
                  ({{ m3State.score }} ×
                  2) + ({{ m4State.score }} × 0.15)</div>
                <div class="trace-line">> 结算结果 = {{ finalScoreRaw }} -> 约束在[0, 100]区间最终得 {{ finalScore }} 分</div>
              </div>
            </div>
          </div>
        </el-collapse-item>

      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const API_BASE = 'http://localhost:8000/api'
const isFetchingData = ref(false)
const availableDates = ref([])
const currentOptions = ref([])
const selectedDate = ref('')
const selectedContract = ref('')
const isLoadingContracts = ref(false)

const diagnosticMode = ref(false)
const activeModules = ref(['m1'])

// 统一表单输入，包含新加的 spreadBp
const form = reactive({
  side: '',
  iv: '', rv: '', ivp: '', termStructure: 'contango',
  iv25dPut: '', iv25dCall: '',
  confidence: '', targetSpace: '', spreadBp: '', depthRatio: '', oi: '',
  delta: '', gamma: '', theta: '', vega: '', premium: '', spot: 65000, equity: 100000, dte: null
})

const m1State = reactive({
  done: false, status: 'gray',
  seller: { score: 0, desc: '', meltdownReason: null, trace: [] },
  buyer: { score: 0, desc: '', meltdownReason: null, trace: [] }
})

const m2State = reactive({ done: false, score: 0, status: 'gray', strategy: '', warning: null, trace: [] })
const m3State = reactive({ done: false, score: 0, status: 'gray', action: '', meltdownReason: null, trace: [] })
const m4State = reactive({ done: false, score: 0, status: 'gray', constraints: [], trace: [] })
const finalScore = ref(0)
const finalScoreRaw = ref(0)
const finalDecision = ref(false)

const validateSideSelected = () => {
  if (!form.side) {
    ElMessage.error('请先在 M1 模块底部确认并选择您要推进的交易路径（买方/卖方）！')
    return false
  }
  return true
}

const triggerMeltdown = () => { diagnosticMode.value = true }

onMounted(async () => {
  isFetchingData.value = true
  try {
    const res = await fetch(`${API_BASE}/dates`)
    const json = await res.json()
    if (json.status === 'success') {
      availableDates.value = json.data
      if (json.data.length > 0) {
        selectedDate.value = json.data[0]
        await fetchOptionsData(json.data[0])
      }
    }
  } catch (error) { ElMessage.error("确保后端在 8000 启动") } finally { isFetchingData.value = false }
})

const fetchOptionsData = async (date) => {
  isFetchingData.value = true; isLoadingContracts.value = true
  selectedContract.value = ''; currentOptions.value = []; resetPipeline()
  try {
    const res = await fetch(`${API_BASE}/options?date=${date}`)
    const json = await res.json()
    if (json.status === 'success') currentOptions.value = json.data
  } catch (error) { ElMessage.error("网络异常") } finally { isFetchingData.value = false; isLoadingContracts.value = false }

  try {
    const expDate = new Date(date); const today = new Date()
    form.dte = Math.max(0, Math.ceil((expDate - today) / (1000 * 60 * 60 * 24)))
  } catch (e) { form.dte = null }
}

const fillContractData = (contractName) => {
  resetPipeline()
  const data = currentOptions.value.find(c => c.instrument_name === contractName)
  if (data) {
    form.spot = data.spot ? Number(data.spot.toFixed(2)) : 0
    form.iv = data.iv ? data.iv.toFixed(4) : ''
    form.delta = data.delta ? data.delta.toFixed(4) : ''
    form.gamma = data.gamma ? data.gamma.toFixed(6) : ''
    form.theta = data.theta ? data.theta.toFixed(4) : ''
    form.vega = data.vega ? data.vega.toFixed(4) : ''

    // 自动填入买卖价差(BP)
    form.spreadBp = (data.spread_bp !== "" && data.spread_bp !== undefined) ? data.spread_bp.toFixed(2) : ''

    // 清空主观数据
    form.rv = ''; form.ivp = ''; form.iv25dPut = ''; form.iv25dCall = ''; form.premium = ''; form.depthRatio = ''; form.oi = ''
  }
}

const resetPipeline = () => {
  diagnosticMode.value = false; activeModules.value = ['m1']; form.side = ''
  m1State.done = false; m1State.status = 'gray'
  m1State.seller = { score: 0, desc: '', meltdownReason: null, trace: [] }
  m1State.buyer = { score: 0, desc: '', meltdownReason: null, trace: [] }
  m2State.done = false; m2State.status = 'gray'; m2State.warning = null; m2State.trace = []
  m3State.done = false; m3State.status = 'gray'; m3State.meltdownReason = null; m3State.trace = []
  m4State.done = false; m4State.status = 'gray'; m4State.constraints = []; m4State.trace = []
  finalDecision.value = false
}

// ================= M1: 双轨并发审计 =================
const auditM1 = () => {
  if (!form.iv || !form.rv || !form.ivp) { ElMessage.warning('请输入 IV, RV 和 IVP'); return }
  diagnosticMode.value = false

  const iv = parseFloat(form.iv) || 0; const rv = parseFloat(form.rv) || 0; const ivp = parseFloat(form.ivp) || 0
  const iv25dPut = parseFloat(form.iv25dPut); const iv25dCall = parseFloat(form.iv25dCall)

  const diff = (iv - rv) * 100
  const skewValid = !isNaN(iv25dPut) && !isNaN(iv25dCall)
  let skewDiff = 0
  if (skewValid) skewDiff = iv25dPut - iv25dCall

  // ------ 结算卖方 ------
  let sScore = 0; let sMeltdown = false; const sTrace = []
  sTrace.push(`【1.1 利差审计】: IV(${iv.toFixed(4)}) - RV(${rv.toFixed(4)}) = ${diff.toFixed(2)}%`)
  if (diff >= 10) { sScore += 10; sTrace.push(`[+] 差值 ≥ 10%，卖方具备丰厚安全垫，得 +10分`); }
  else if (diff >= 5) { sScore += 7; sTrace.push(`[+] 5% ≤ 差值 < 10%，标准溢价，得 +7分`); }
  else if (diff <= -90) { sScore -= 20; sMeltdown = true; sTrace.push(`[-] 差值极度倒挂，触发卖方熔断机制 (-20分)`); }
  else { sTrace.push(`[=] 利差不足 5%，卖方无溢价，得 0 分`); }

  sTrace.push(`【1.2 波动率锥】: 当前 IV 分位值为 ${(ivp * 100).toFixed(0)}%`)
  if (ivp >= 0.5 && ivp <= 0.8) { sScore += 10; sTrace.push(`[+] 处于 50%-80% 黄金做空区间，得 +10分`); }
  else if (ivp >= 0.9) { sScore -= 20; sMeltdown = true; sTrace.push(`[-] IVP ≥ 90%，事出反常必有妖，防守熔断 (-20分)`); }

  sTrace.push(`【1.3 期限结构】: 状态为 ${form.termStructure === 'backwardation' ? '贴水(近>远)' : '升水(近<远)'}`)
  if (form.termStructure === 'backwardation') { sScore += 10; sTrace.push(`[+] 期限结构贴水有利于卖方吃近月，得 +10分`); }

  if (skewValid) {
    sTrace.push(`【1.4 Skew曲面】: 25D Put(${iv25dPut}) - 25D Call(${iv25dCall}) = ${skewDiff.toFixed(4)}`)
    if (skewDiff > 0) { sScore += 10; sTrace.push(`[+] 差值大于0，恐慌溢价更高，建议 卖出 Put，得 +10分`); }
    else if (skewDiff < 0) { sScore += 10; sTrace.push(`[+] 差值小于0，贪婪溢价更高，建议 卖出 Call，得 +10分`); }
    else { sTrace.push(`[=] Skew无偏斜，得 0 分`); }
  } else { sTrace.push(`【1.4 Skew曲面】: 数据不全，跳过评估 (得 0 分)`); }

  m1State.seller.score = sScore; m1State.seller.trace = sTrace
  m1State.seller.desc = sScore >= 35 ? "优质区" : (sScore >= 25 ? "标准区" : "恶劣区")
  if (sMeltdown || sScore < 20) { m1State.seller.meltdownReason = "卖方指标崩盘"; triggerMeltdown(); }

  // ------ 结算买方 ------
  let bScore = 0; let bMeltdown = false; const bTrace = []
  bTrace.push(`【1.1 利差审计】: IV(${iv.toFixed(4)}) - RV(${rv.toFixed(4)}) = ${diff.toFixed(2)}%`)
  if (rv > iv && diff < 0) { bScore += 10; bTrace.push(`[+] RV > IV 且差值 < 0，买入便宜波动率，得 +10分`); }
  else { bTrace.push(`[=] 未满足 RV > IV 差值 < 0，得 0 分`); }

  bTrace.push(`【1.2 波动率锥】: 当前 IV 分位值为 ${(ivp * 100).toFixed(0)}%`)
  if (ivp < 0.25) { bScore += 10; bTrace.push(`[+] 处于极度低估区间 (<25%)，得 +10分`); }
  else { bTrace.push(`[=] 未处于低估区间，得 0 分`); }

  bTrace.push(`【1.3 期限结构】: 状态为 ${form.termStructure === 'backwardation' ? '贴水(近>远)' : '升水(近<远)'}`)
  if (form.termStructure === 'contango') { bScore += 10; bTrace.push(`[+] 期限结构升水，有利于买方爆发，得 +10分`); }

  if (skewValid) {
    bTrace.push(`【1.4 Skew曲面】: 25D Put(${iv25dPut}) - 25D Call(${iv25dCall}) = ${skewDiff.toFixed(4)}`)
    if (skewDiff > 0) { bScore += 10; bTrace.push(`[+] 差值大于0，看跌期权贵，建议逆向 买入 Call，得 +10分`); }
    else if (skewDiff < 0) { bScore += 10; bTrace.push(`[+] 差值小于0，看涨期权贵，建议逆向 买入 Put，得 +10分`); }
    else { bTrace.push(`[=] Skew无偏斜，得 0 分`); }
  } else { bTrace.push(`【1.4 Skew曲面】: 数据不全，跳过评估 (得 0 分)`); }

  m1State.buyer.score = bScore; m1State.buyer.trace = bTrace
  m1State.buyer.desc = bScore >= 30 ? "搏击区" : (bScore === 20 ? "鸡肋区" : "垃圾时间")
  if (bScore < 20) { bMeltdown = true; triggerMeltdown(); m1State.buyer.meltdownReason = "买方赔率丧失"; }

  m1State.done = true
}

// ================= M2: 策略选型 =================
const auditM2 = () => {
  if (!validateSideSelected()) return;
  if (!form.confidence || !form.targetSpace) { ElMessage.warning('请选择所有条件'); return }

  let score = 0; let bScore = 0; const traceLog = []
  const confVal = parseInt(form.confidence); const spaceVal = parseInt(form.targetSpace)
  const ivp = parseFloat(form.ivp) || 0

  traceLog.push(`【A项 信心强度】: 选中项分值 -> ${confVal} 分`)
  traceLog.push(`【C项 目标空间】: 选中项分值 -> ${spaceVal} 分`)

  traceLog.push(`【B项 IV成本审计】: 当前 IV 分位为 ${(ivp * 100).toFixed(0)}%`)
  if (ivp < 0.25) { bScore = 30; traceLog.push(`[+] 处于极便宜区间 (<25%)，支持裸买单腿，得 +30分`); }
  else if (ivp <= 0.5) { bScore = 15; traceLog.push(`[+] 处于中等成本 (25-50%)，建议使用双腿价差摊薄成本，得 +15分`); }
  else { bScore = 0; traceLog.push(`[-] IV 昂贵 (>50%)，不得裸买，得 0 分`); }

  score = confVal + spaceVal + bScore
  traceLog.push(`====> M2 权重总分: ${confVal}(信心) + ${spaceVal}(空间) + ${bScore}(成本) = ${score} 分`)

  if (score >= 80) { m2State.strategy = "强制单腿"; m2State.status = 'green'; traceLog.push("结论: 总分≥80，系统自动锁定单腿"); }
  else if (score >= 50) { m2State.strategy = "标准价差 (30%对冲)"; m2State.status = 'green'; traceLog.push("结论: 50≤总分<80，加载价差模板"); }
  else if (score >= 30) { m2State.strategy = "复合结构 (铁鹰/铁蝶)"; m2State.status = 'yellow'; traceLog.push("结论: 30≤总分<50，启用两端保护"); }
  else { m2State.strategy = "三重否定拦截"; m2State.status = 'red'; triggerMeltdown(); traceLog.push("结论: 分数<30，赔率丧失，触发红灯！"); }

  m2State.trace = traceLog; m2State.score = score; m2State.done = true
}

// ================= M3: 流动性 =================
const auditM3 = () => {
  if (!validateSideSelected()) return;
  let score = 0; const traceLog = []
  const bp = parseFloat(form.spreadBp || 0); const depth = parseFloat(form.depthRatio || 0)

  traceLog.push(`【流动性摩擦审计】: API解析价差为 ${bp} BP`)
  if (bp <= 15) { score += 15; traceLog.push(`[+] 极佳摩擦成本，得 +15分`); }
  else if (bp <= 30) { score += 10; traceLog.push(`[+] 正常摩擦成本，得 +10分`); }
  else if (bp <= 60) { score += 5; traceLog.push(`[+] 滑点警告：建议冰山委托，得 +5分`); }
  else { traceLog.push(`[-] 价差超限自杀式摩擦，记 0 分！`); triggerMeltdown(); }

  traceLog.push(`【盘口深度审计】: 挂单与计划量比率为 ${depth} 倍`)
  if (depth > 10) { score += 10; traceLog.push(`[+] 深度极佳 (>10倍)，得 +10分`); }
  else if (depth >= 5) { score += 7; traceLog.push(`[+] 深度正常 (5-10倍)，得 +7分`); }
  else if (depth >= 2) { score += 3; traceLog.push(`[+] 深度较浅 (2-5倍)，分步成交，得 +3分`); }
  else { traceLog.push(`[-] 盘口太脆，直接记 0 分！`); triggerMeltdown(); }

  traceLog.push(`====> M3 合计分: ${score} 分`)
  if (score >= 25) { m3State.action = "允许市价单"; m3State.status = 'green' }
  else if (score >= 15) { m3State.action = "强制限价动态中间价"; m3State.status = 'yellow' }
  else { m3State.action = "高危：禁止开仓"; m3State.status = 'red'; triggerMeltdown(); }

  m3State.trace = traceLog; m3State.score = score; m3State.done = true
}

// ================= M4: 希腊字母约束 =================
const auditM4 = () => {
  if (!validateSideSelected()) return;
  const constraints = []; const traceLog = []; let allPass = true
  const delta = parseFloat(form.delta || 0); const gamma = parseFloat(form.gamma || 0)
  const spot = parseFloat(form.spot || 0); const iv = parseFloat(form.iv || 0)

  if (form.side === 'seller') {
    traceLog.push(`【卖方 Gamma 防爆审计】:`)
    traceLog.push(`-> 公式: Gamma(${gamma.toFixed(6)}) * Spot(${spot}) * IV(${iv.toFixed(4)}) * 0.2876`)
    const gammaRisk = gamma * spot * iv * 0.2876
    const deltaAbs = Math.abs(delta)
    traceLog.push(`-> RiskValue 绝对值 = ${gammaRisk.toFixed(4)}`)
    traceLog.push(`-> 头寸基准 |Delta| = ${deltaAbs.toFixed(4)}`)
    const passGamma = gammaRisk < deltaAbs
    if (passGamma) traceLog.push(`✅ 判定: RiskValue < Delta，防爆校验通过。`)
    else { traceLog.push(`❌ 判定: RiskValue 越过阈值，方向反转将摧毁对冲。`); allPass = false; }
    constraints.push({ name: 'Gamma防爆', pass: passGamma, desc: passGamma ? '校验通过' : '防爆线被击穿' })
  } else {
    traceLog.push(`【买方 Delta 杠杆审计】:`)
    traceLog.push(`-> 提取API原生 Delta = ${delta.toFixed(4)}`)
    const deltaAbs = Math.abs(delta)
    const passDelta = deltaAbs >= 0.4 && deltaAbs <= 0.5
    traceLog.push(`-> 准则: 仅接受平值/微虚值 (0.4 ≤ |Delta| ≤ 0.5)`)
    if (passDelta) traceLog.push(`✅ 判定: 现有头寸符合攻击位置。`)
    else { traceLog.push(`❌ 判定: Delta偏离指定攻击区间。`); allPass = false; }
    constraints.push({ name: 'Delta甜点', pass: passDelta, desc: passDelta ? '位置优良' : '偏离平值' })
  }

  m4State.trace = traceLog; m4State.constraints = constraints
  m4State.score = allPass ? 100 : 0; m4State.status = allPass ? 'green' : 'red'
  if (!allPass) triggerMeltdown()
  m4State.done = true
}

// ================= M6: 动态汇总 =================
const currentM1Score = computed(() => {
  return form.side === 'seller' ? m1State.seller.score : m1State.buyer.score
})

const generateFinalDecision = () => {
  if (!validateSideSelected()) return;
  const weighted = (currentM1Score.value * 3) + (m2State.score * 0.25) + (m3State.score * 2) + (m4State.score * 0.15)
  finalScoreRaw.value = weighted.toFixed(2)
  finalScore.value = Math.min(100, Math.max(0, Math.round(weighted)))
  finalDecision.value = true
}

const finalActionType = computed(() => {
  if (finalScore.value >= 85) return 'success'; if (finalScore.value >= 70) return 'primary'
  if (finalScore.value >= 50) return 'warning'; return 'danger'
})

const finalActionText = computed(() => {
  if (form.side === 'buyer') {
    if (finalScore.value >= 85) return '全仓单腿 + 杠杆系数 1.5x'
    if (finalScore.value >= 70) return '标准仓位 + 价差保护'
    if (finalScore.value >= 50) return '仅允许模拟盘沙盘推演'
    return '系统强烈建议放弃本次交易'
  } else {
    if (finalScore.value >= 85) return '标准仓位 + IV 溢价捕获'
    if (finalScore.value >= 70) return '仓位×0.8 + 自动展期设置'
    if (finalScore.value >= 50) return '仓位×0.5 + 强制 Gamma 对冲'
    return '高危！仅显示撤退防守方案'
  }
})
</script>

<style scoped>
.theme-buyer {
  --sys-primary: #409EFF;
  --sys-bg: #ecf5ff;
  --sys-border: #b3d8ff;
}

.theme-seller {
  --sys-primary: #E6A23C;
  --sys-bg: #fdf6ec;
  --sys-border: #f3d19e;
}

.theme-neutral {
  --sys-primary: #909399;
  --sys-bg: #f4f4f5;
  --sys-border: #dcdfe6;
}

.audit-container {
  padding: 20px;
  max-width: 1300px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
}

.master-card {
  border-top: 4px solid var(--sys-primary);
  transition: all 0.3s;
}

.global-control-panel {
  background: var(--sys-bg);
  padding: 20px 20px 10px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid var(--sys-border);
}

.role-card {
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  height: 100%;
  background: #fff;
}

.seller-card {
  border-top: 3px solid #E6A23C;
}

.buyer-card {
  border-top: 3px solid #409EFF;
}

.score-display {
  font-size: 16px;
  margin: 10px 0;
}

.score-display strong {
  font-size: 22px;
}

.module-block {
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
}

.module-title {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  width: 100%;
}

.step-num {
  display: inline-block;
  background: #303133;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 10px;
  font-size: 14px;
}

.module-content {
  padding: 20px;
  background: #fafafa;
  border-top: 1px dashed #dcdfe6;
}

.trace-log {
  background-color: #1e1e1e;
  color: #a9dc76;
  font-family: 'Courier New', monospace;
  padding: 15px;
  border-radius: 6px;
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.6;
  border-left: 4px solid var(--sys-primary);
}

.trace-title {
  color: #ffd866;
  font-weight: bold;
  margin-bottom: 10px;
  font-size: 14px;
}

.trace-line {
  margin-bottom: 4px;
  white-space: pre-wrap;
}

.status-light {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-left: auto;
  margin-right: 15px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  transition: background 0.3s;
}

.bg-gray {
  background-color: #C0C4CC;
}

.bg-green {
  background-color: #67C23A;
  box-shadow: 0 0 8px #67C23A;
}

.bg-yellow {
  background-color: #E6A23C;
  box-shadow: 0 0 8px #E6A23C;
}

.bg-red {
  background-color: #F56C6C;
  box-shadow: 0 0 10px #F56C6C;
  animation: pulse 1.5s infinite;
}

.meltdown-alert {
  margin-bottom: 20px;
  border-left: 5px solid #F56C6C;
}

.decision-board {
  text-align: center;
  background: var(--sys-bg);
  padding: 30px;
  border: 2px dashed var(--sys-primary);
  border-radius: 8px;
}

.score-huge {
  font-size: 48px;
  font-weight: 900;
  color: var(--sys-primary);
}

.w-full {
  width: 100%;
}

.mt-10 {
  margin-top: 10px;
}

.mt-15 {
  margin-top: 15px;
}

.mt-20 {
  margin-top: 20px;
}

.mb-10 {
  margin-bottom: 10px;
}

.mb-15 {
  margin-bottom: 15px;
}

.center {
  text-align: center;
}

.text-red {
  color: #F56C6C;
  font-weight: bold;
}

.text-green {
  color: #67C23A;
  font-weight: bold;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>