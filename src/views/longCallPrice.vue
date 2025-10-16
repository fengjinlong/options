<script setup lang="ts">
import { ref, computed } from "vue";

// 基础输入
const spot_price = ref<number | null>(null); // 当前现价 S
const strike_price = ref<number | null>(null); // 行权价 p₁
const expiry_date = ref<string | null>(null); // 到期日
const current_iv = ref<number | null>(null); // 当前IV(%) iv₁
const atm_iv = ref<number | null>(null); // 同期限ATM IV(%)
const price_7d_ago = ref<number | null>(null); // 七天前现价

// 高级模式
const advanced_mode = ref<boolean>(false);
const iv_low = ref<number | null>(null); // 历史最低IV(%) iv₂
const price_at_iv_low = ref<number | null>(null); // 当时价格 p₂

// 工具函数
function daysDiffFromToday(targetISO: string): number {
  const start = new Date();
  const end = new Date(targetISO);
  // 归零时分秒，避免日界偏差
  start.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);
  const ms = end.getTime() - start.getTime();
  return Math.max(0, Math.floor(ms / (24 * 3600 * 1000)));
}

const days_to_expiry = computed<number>(() =>
  expiry_date.value ? daysDiffFromToday(expiry_date.value) : 0
);
const T = computed<number>(() => days_to_expiry.value / 365);

const toDecimal = (v: number): number => (v > 10 ? v / 100 : v);

const fmtPct = (v: number, digits = 0): string =>
  `${(v * 100).toFixed(digits)}%`;

const results = computed(() => {
  const iv1 = toDecimal(current_iv.value ?? 0);
  const ivATM = toDecimal(atm_iv.value ?? 0);
  const iv2 = toDecimal(iv_low.value ?? 0);

  const S = spot_price.value ?? 0;
  const p1 = strike_price.value ?? 0;
  const p2 = price_at_iv_low.value ?? 0;
  const price7 = price_7d_ago.value ?? 0;
  const Tval = T.value || 0.0001;

  const iv_premium = ivATM > 0 ? (iv1 - ivATM) / ivATM : 0;
  const required_move = S > 0 ? p1 / S - 1 : 0;
  const expected_move = iv1 * Math.sqrt(Tval);
  const z = expected_move > 0 ? required_move / expected_move : 0;
  const trend = price7 > 0 ? (S - price7) / price7 : 0;
  const trend_factor = 1 + 0.5 * trend;
  const time_penalty = days_to_expiry.value < 14 ? 15 : 0;

  const absTrend = Math.abs(trend);
  const IV_score =
    iv_premium <= 0.1
      ? 100
      : iv_premium <= 0.3
      ? 70
      : iv_premium <= 0.6
      ? 40
      : 10;
  const Reach_score = z <= 0.75 ? 100 : z <= 1.5 ? 70 : z <= 2 ? 40 : 10;
  const Trend_score =
    absTrend <= 0.1 ? 100 : absTrend <= 0.3 ? 70 : absTrend <= 0.6 ? 40 : 10;

  let iv_risk_factor = 1;
  if (advanced_mode.value) {
    const iv_hist_premium = iv2 > 0 ? (iv1 - iv2) / iv2 : 0;
    const price_diff = p2 > 0 ? (S - p2) / p2 : 0;
    iv_risk_factor =
      1 -
      Math.min(Math.max(iv_hist_premium, 0), 1) * 0.4 -
      Math.min(Math.max(price_diff, 0), 1) * 0.2;
  }

  let base_score = 0.4 * IV_score + 0.4 * Reach_score + 0.2 * Trend_score;
  let final_score = base_score * trend_factor * iv_risk_factor - time_penalty;
  final_score = Math.max(0, Math.min(100, final_score));

  const label =
    final_score >= 70
      ? "✅ 性价比高"
      : final_score >= 50
      ? "⚠️ 中性"
      : "❌ 谨慎";

  return {
    iv_premium,
    required_move,
    expected_move,
    z,
    trend,
    trend_factor,
    IV_score,
    Reach_score,
    Trend_score,
    iv_risk_factor,
    final_score,
    label,
  };
});

// 颜色函数（红→黄→绿）
const scoreColor = (score: number) => {
  if (score < 50) return "#f56c6c"; // 红
  if (score < 70) return "#e6a23c"; // 黄
  return "#67c23a"; // 绿
};

function resetAll() {
  spot_price.value = null;
  strike_price.value = null;
  expiry_date.value = null;
  current_iv.value = null;
  atm_iv.value = null;
  price_7d_ago.value = null;
  advanced_mode.value = false;
  iv_low.value = null;
  price_at_iv_low.value = null;
}

async function copyResult() {
  const r = results.value;
  const lines = [
    "🧮 期权性价比评估结果：",
    "────────────────────────────",
    `IV 溢价：${fmtPct(r.iv_premium, 0)}`,
    `达标难度（z）：${r.z.toFixed(2)}`,
    `趋势修正：${fmtPct(r.trend_factor - 1, 0)}`,
  ];
  if (advanced_mode.value) {
    lines.push(`历史IV高估修正系数：${r.iv_risk_factor.toFixed(2)}`);
  }
  lines.push(
    "",
    `综合得分：${r.final_score.toFixed(0)} / 100`,
    `性价比标签：${r.label}`
  );
  const text = lines.join("\n");
  try {
    await navigator.clipboard.writeText(text);
  } catch (e) {
    // 兼容不支持 clipboard 的环境
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
  }
}
</script>

<template>
  <div class="page">
    <div class="title">
      <h2>看涨期权性价比评估（前端本地计算）</h2>
      <p>
        输入期权关键参数，系统自动计算 IV
        溢价、达标难度、趋势修正，并输出综合得分与建议。所有数据仅在浏览器端计算，不发起任何网络请求。
      </p>
    </div>

    <el-card class="card" shadow="hover">
      <template #header>
        <div class="card-header">表单输入</div>
      </template>
      <el-form label-width="120px">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="当前现价 (S)" :title="'当前标的现价'">
              <el-input-number
                v-model="spot_price"
                :min="0"
                :step="0.01"
                placeholder="请输入现价，如 150"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="行权价 (p₁)" :title="'期权目标行权价'">
              <el-input-number
                v-model="strike_price"
                :min="0"
                :step="0.01"
                placeholder="请输入行权价，如 200"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="到期日" :title="'自动计算剩余天数'">
              <el-date-picker
                v-model="expiry_date"
                type="date"
                placeholder="选择到期日"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="当前IV (%)" :title="'该行权价的隐含波动率'">
              <el-input-number
                v-model="current_iv"
                :min="0"
                :max="1000"
                :step="0.1"
                placeholder="如 80（表示80%）"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="ATM IV (%)" :title="'同期限平值IV'">
              <el-input-number
                v-model="atm_iv"
                :min="0"
                :max="1000"
                :step="0.1"
                placeholder="如 60（表示60%）"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="七天前现价" :title="'用于趋势修正'">
              <el-input-number
                v-model="price_7d_ago"
                :min="0"
                :step="0.01"
                placeholder="如 140"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider />
        <el-form-item label="📊 开启高级评估">
          <el-switch v-model="advanced_mode" />
        </el-form-item>

        <el-row v-show="advanced_mode" :gutter="16">
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="历史最低IV (%)" :title="'最近一个月的IV低点'">
              <el-input-number
                v-model="iv_low"
                :min="0"
                :max="1000"
                :step="0.1"
                placeholder="如 50"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="当时价格 (p₂)" :title="'IV低点对应的标的价格'">
              <el-input-number
                v-model="price_at_iv_low"
                :min="0"
                :step="0.01"
                placeholder="如 120"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="actions">
          <el-button type="primary" @click="resetAll">重置</el-button>
          <el-button @click="copyResult">复制结果</el-button>
        </div>
      </el-form>
    </el-card>

    <el-row :gutter="16" class="mt-16">
      <el-col :xs="24" :md="14">
        <el-card class="card" shadow="hover">
          <template #header>
            <div class="card-header">实时计算</div>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="剩余天数"
              >{{ days_to_expiry }} 天</el-descriptions-item
            >
            <el-descriptions-item label="IV 溢价">{{
              fmtPct(results.iv_premium, 0)
            }}</el-descriptions-item>
            <el-descriptions-item label="达标难度（z）">{{
              results.z.toFixed(2)
            }}</el-descriptions-item>
            <el-descriptions-item label="趋势修正">{{
              fmtPct(results.trend_factor - 1, 0)
            }}</el-descriptions-item>
            <el-descriptions-item
              v-if="advanced_mode"
              label="历史IV高估修正系数"
              >{{ results.iv_risk_factor.toFixed(2) }}</el-descriptions-item
            >
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10">
        <el-card class="card" shadow="hover">
          <template #header>
            <div class="card-header">结果卡片</div>
          </template>

          <div class="score">
            <div class="score-line">
              <span>综合得分</span>
              <strong>{{ results.final_score.toFixed(0) }}</strong>
            </div>
            <el-progress
              :percentage="Number(results.final_score.toFixed(0))"
              :stroke-width="16"
              :color="scoreColor(results.final_score)"
            />
            <div class="label">{{ results.label }}</div>
            <div class="advice">
              <template v-if="results.final_score >= 70">
                建议：可考虑买入 / 分批参与。
              </template>
              <template v-else-if="results.final_score >= 50">
                建议：可用价差或等待更优时机。
              </template>
              <template v-else> 建议：不建议裸买 / 考虑观望。 </template>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="card mt-16" shadow="never">
      <el-collapse>
        <el-collapse-item name="1">
          <template #title>展开查看计算细节</template>
          <div class="details">
            <p>T = 剩余天数 / 365 = {{ days_to_expiry }} / 365</p>
            <p>
              iv_premium = (iv₁ - iv_ATM) / iv_ATM =
              {{ fmtPct(results.iv_premium, 0) }}
            </p>
            <p>required_move = (p₁ / S) - 1</p>
            <p>expected_move = iv₁ × sqrt(T)</p>
            <p>
              z = required_move / expected_move = {{ results.z.toFixed(2) }}
            </p>
            <p>trend = (S - 7天前价格) / 7天前价格</p>
            <p>
              trend_factor = 1 + 0.5 × trend =
              {{ (results.trend_factor - 1).toFixed(2) }}
            </p>
            <p>time_penalty = 剩余天数小于14天时为 15 分，否则 0 分</p>
            <p>IV_score / Reach_score / Trend_score 按区间赋分</p>
            <p v-if="advanced_mode">
              iv_risk_factor = 1 - min(iv_hist_premium,1)×0.4 -
              min(price_diff,1)×0.2
            </p>
            <p>
              final_score = 0.4×IV_score + 0.4×Reach_score +
              0.2×Trend_score，之后乘以 trend_factor 与 iv_risk_factor，再减
              time_penalty，并限制在 0~100
            </p>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <el-row :gutter="16" class="mt-16">
      <el-col :xs="24" :md="12">
        <el-card class="card" shadow="never">
          <template #header>
            <div class="card-header">指标说明</div>
          </template>
          <ul class="notes">
            <li>
              <strong>IV 溢价</strong>：相对同期限 ATM
              的隐含波动率溢价。越低越好，表示不为虚值权利金支付过多波动率。
            </li>
            <li>
              <strong>达标难度 z</strong
              >：到期达到行权价所需涨幅与期望波动的比值。越小越好，代表更容易达成。
            </li>
            <li>
              <strong>趋势修正</strong>：根据近 7
              天价格变化对得分的乘数修正；上涨趋势略有加分，下跌趋势略有减分。
            </li>
            <li>
              <strong>时间惩罚</strong>：剩余少于 14 天时减分，用于提醒短期
              Theta 与不确定性影响。
            </li>
            <li>
              <strong>历史IV高估修正</strong>（高级）：当前 IV
              相对近低点偏高、且价格相对当时更高时，给予额外折减，降低追高风险。
            </li>
          </ul>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="card" shadow="never">
          <template #header>
            <div class="card-header">评估说明</div>
          </template>
          <ul class="notes">
            <li>
              <strong>✅ 性价比高</strong>：综合得分≥70。通常意味着较合理的 IV
              与达标难度，可考虑买入或分批参与。
            </li>
            <li>
              <strong>⚠️ 中性</strong
              >：50≤综合得分&lt;70。可考虑价差策略、等待更优 IV 或价格位置。
            </li>
            <li>
              <strong>❌ 谨慎</strong>：综合得分&lt;50。多为高 IV
              或达标难度偏高的组合，不建议裸买。
            </li>
            <li>
              本工具为启发式评估，未考虑利率、股息、精确希腊、流动性与滑点等因素，结果仅供参考，不构成投资建议。
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page {
  padding: 16px;
}
.title {
  margin-bottom: 12px;
}
.card {
  margin-top: 8px;
}
.card-header {
  font-weight: 600;
}
.actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}
.mt-16 {
  margin-top: 16px;
}
.score {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.score-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.label {
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}
.advice {
  color: #606266;
  text-align: center;
}
.notes {
  margin: 0;
  padding-left: 18px;
  color: #606266;
  line-height: 1.6;
}
</style>
