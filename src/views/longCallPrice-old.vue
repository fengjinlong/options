<template>
  <main class="container">
    <h2>🧮 期权性价比评估工具</h2>

    <section class="form-grid">
      <label title="当前标的最新价格。例如：120">
        当前现价 (S)：
        <input
          inputmode="decimal"
          v-model.number="spot_price"
          placeholder="示例：120"
        />
      </label>

      <label title="期权行权价。例如：150">
        行权价 (p₁)：
        <input
          inputmode="decimal"
          v-model.number="strike_price"
          placeholder="示例：150"
        />
      </label>

      <label title="选择期权到期日，系统自动计算剩余天数">
        到期日：
        <input type="date" v-model="expiry_date" />
      </label>

      <div class="days" title="到期日 - 今日（按自然日计算）">
        剩余天数：<strong>{{ days_to_expiry }}</strong> 天
      </div>

      <label
        title="该行权价对应的隐含波动率。可输入百分比或小数：120 或 1.2 均可"
      >
        当前 IV (%)：
        <input
          inputmode="decimal"
          v-model.number="current_iv"
          placeholder="示例：120 或 1.2"
        />
      </label>

      <label title="同到期日平值(ATM)隐含波动率。可输入百分比或小数">
        ATM IV (%)：
        <input
          inputmode="decimal"
          v-model.number="atm_iv"
          placeholder="示例：100 或 1.0"
        />
      </label>

      <label title="用于趋势修正，输入 7 天前的标的现价">
        七天前现价：
        <input
          inputmode="decimal"
          v-model.number="price_7d_ago"
          placeholder="示例：110"
        />
      </label>

      <div class="actions">
        <button type="button" @click="onReset">重置</button>
        <button type="button" @click="onCopy">复制结果</button>
      </div>
    </section>

    <hr />

    <section class="middle" aria-live="polite">
      <h3>中间变量</h3>
      <ul class="kv">
        <li title="(iv1 - iv_ATM) / iv_ATM">
          IV 溢价：<strong>{{ formatPct(results.iv_premium) }}</strong>
        </li>
        <li title="(p₁ / S) - 1">
          需涨幅：<strong>{{ formatPct(results.required_move) }}</strong>
        </li>
        <li title="iv1 * sqrt(T)">
          预期波幅(1σ)：<strong>±{{ formatPct(results.expected_move) }}</strong>
        </li>
        <li title="required_move / expected_move">
          难度指标 z 值：<strong>{{ results.z.toFixed(2) }}</strong>
        </li>
        <li title="(S - price_7d_ago) / price_7d_ago">
          趋势：<strong>{{ formatPct(results.trend) }}</strong>
        </li>
        <li title="days_to_expiry / 365">
          年化到期时间 T：<strong>{{ T.toFixed(4) }}</strong>
        </li>
      </ul>
    </section>

    <section class="results">
      <h3>结果</h3>

      <div class="contract-meta">
        <span>标的现价：{{ spot_price || "-" }}</span>
        <span>· 行权价：{{ strike_price || "-" }}</span>
        <span>· 到期：{{ expiry_date || "-" }}</span>
        <span>· 剩余：{{ days_to_expiry }} 天</span>
      </div>

      <div class="scorebar" :title="'最终得分，趋势与时间惩罚修正后'">
        <div
          class="bar"
          :style="{ width: barWidth, background: barColor }"
        ></div>
      </div>
      <p class="score-text">
        最终得分：<strong>{{ results.final_score_adj.toFixed(1) }}/100</strong>
      </p>
      <p class="label" :class="labelClass">{{ results.label }}</p>

      <details class="details">
        <summary>展开计算细节</summary>
        <div class="grid-2">
          <div>
            <h4>原始输入</h4>
            <ul class="kv">
              <li>
                当前现价 S：<strong>{{ spot_price ?? "-" }}</strong>
              </li>
              <li>
                行权价 p₁：<strong>{{ strike_price ?? "-" }}</strong>
              </li>
              <li>
                到期日：<strong>{{ expiry_date ?? "-" }}</strong>
              </li>
              <li>
                七天前现价：<strong>{{ price_7d_ago ?? "-" }}</strong>
              </li>
              <li>
                当前 IV：<strong>{{ current_iv ?? "-" }}</strong>
              </li>
              <li>
                ATM IV：<strong>{{ atm_iv ?? "-" }}</strong>
              </li>
            </ul>
          </div>
          <div>
            <h4>评分分解</h4>
            <ul class="kv">
              <li>
                IV 评分：<strong>{{ results.IV_score }}</strong>
              </li>
              <li>
                达标难度评分：<strong>{{ results.Reach_score }}</strong>
              </li>
              <li>
                趋势评分：<strong>{{ results.Price_score }}</strong>
              </li>
              <li>
                趋势修正因子：<strong>{{
                  results.trend_factor.toFixed(3)
                }}</strong>
              </li>
              <li>
                时间惩罚：<strong>{{ time_penalty }}</strong>
              </li>
            </ul>
          </div>
        </div>
      </details>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

const spot_price = ref<number | null>(null);
const strike_price = ref<number | null>(null);
const current_iv = ref<number | null>(null);
const atm_iv = ref<number | null>(null);
const expiry_date = ref<string | null>(null);
const price_7d_ago = ref<number | null>(null);

function daysBetweenToday(expiry: string | null): number {
  if (!expiry) return 0;
  const today = new Date();
  const end = new Date(expiry + "T00:00:00");
  const ms =
    end.getTime() -
    new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
  const days = Math.floor(ms / (24 * 3600 * 1000));
  return Math.max(0, days);
}

const days_to_expiry = computed<number>(() =>
  daysBetweenToday(expiry_date.value)
);
const T = computed<number>(() => days_to_expiry.value / 365);

function toDecimal(v: number): number {
  if (!isFinite(v)) return 0;
  return v > 10 ? v / 100 : v;
}

const results = computed(() => {
  const iv1 = toDecimal(current_iv.value ?? 0);
  const ivATM = toDecimal(atm_iv.value ?? 0);
  const S = spot_price.value ?? 0;
  const p1 = strike_price.value ?? 0;
  const price7 = price_7d_ago.value ?? 0;
  const Tval = T.value || 0.0001;

  const iv_premium = ivATM ? (iv1 - ivATM) / ivATM : 0;
  const required_move = S ? p1 / S - 1 : 0;
  const expected_move = iv1 * Math.sqrt(Tval);
  const z = expected_move > 0 ? required_move / expected_move : 0;
  const trend = price7 ? (S - price7) / price7 : 0;
  const trend_factor = 1 + 0.5 * trend;
  const time_penalty_local = days_to_expiry.value < 14 ? 15 : 0;

  const IV_score =
    iv_premium <= 0.1
      ? 100
      : iv_premium <= 0.3
      ? 70
      : iv_premium <= 0.6
      ? 40
      : 10;
  const Reach_score = z <= 0.75 ? 100 : z <= 1.5 ? 70 : z <= 2 ? 40 : 10;
  const Price_score =
    Math.abs(trend) <= 0.1
      ? 100
      : Math.abs(trend) <= 0.3
      ? 70
      : Math.abs(trend) <= 0.6
      ? 40
      : 10;

  let final_score = 0.4 * IV_score + 0.4 * Reach_score + 0.2 * Price_score;
  let final_score_adj = final_score * trend_factor - time_penalty_local;
  final_score_adj = Math.max(0, Math.min(100, final_score_adj));

  const label =
    final_score_adj >= 70
      ? "✅ 性价比高"
      : final_score_adj >= 50
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
    Price_score,
    final_score_adj,
    label,
  };
});

const barWidth = computed(() => `${results.value.final_score_adj.toFixed(1)}%`);
const barColor = computed(
  () => "linear-gradient(90deg, #ef4444, #f59e0b, #10b981)"
);

const labelClass = computed(() => {
  const s = results.value.final_score_adj;
  if (s >= 70) return "good";
  if (s >= 50) return "neutral";
  return "bad";
});

const time_penalty = computed(() => (days_to_expiry.value < 14 ? 15 : 0));

function formatPct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

async function onCopy() {
  const payload = {
    input: {
      spot_price: spot_price.value,
      strike_price: strike_price.value,
      expiry_date: expiry_date.value,
      days_to_expiry: days_to_expiry.value,
      current_iv: current_iv.value,
      atm_iv: atm_iv.value,
      price_7d_ago: price_7d_ago.value,
    },
    computed: results.value,
  };
  const text = JSON.stringify(payload, null, 2);
  try {
    await navigator.clipboard.writeText(text);
    alert("结果已复制到剪贴板");
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    alert("结果已复制到剪贴板");
  }
}

function onReset() {
  spot_price.value = null;
  strike_price.value = null;
  current_iv.value = null;
  atm_iv.value = null;
  price_7d_ago.value = null;
  expiry_date.value = null;
}
</script>

<style scoped>
.container {
  max-width: 720px;
  margin: 0 auto;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial,
    sans-serif;
  padding: 16px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: end;
}
.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
}
.form-grid input {
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}
.form-grid .days {
  align-self: center;
  font-size: 14px;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.actions button {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}
.actions button:hover {
  background: #f3f4f6;
}

.middle {
  background: #f9fafb;
  padding: 12px;
  border-radius: 12px;
  margin-top: 12px;
}
.kv {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 12px;
}
.kv li {
  font-size: 14px;
}

.results {
  background: #f9fafb;
  padding: 16px;
  border-radius: 12px;
  margin-top: 16px;
}
.contract-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  color: #374151;
  font-size: 14px;
  margin-bottom: 8px;
}
.scorebar {
  position: relative;
  height: 16px;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}
.scorebar .bar {
  height: 100%;
  transition: width 0.4s ease;
}
.score-text {
  font-size: 16px;
  margin-top: 10px;
}
.label {
  font-weight: bold;
  margin-top: 4px;
}
.label.good {
  color: #059669;
}
.label.neutral {
  color: #d97706;
}
.label.bad {
  color: #dc2626;
}
.details {
  margin-top: 12px;
}
.details summary {
  cursor: pointer;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .kv {
    grid-template-columns: 1fr;
  }
  .grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>
