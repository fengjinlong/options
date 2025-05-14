<script setup lang="ts">
import { ref, computed } from "vue";

const currentPrice = ref("");
const volatility = ref("");
const expiryDate = ref("");
const showResult = ref(false);

// Format today's date
const todayFormatted = computed(() => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
});

// Calculate days to expiry based on selected date
const daysToExpiry = computed(() => {
  if (!expiryDate.value) return 0;
  const today = new Date();
  const expiry = new Date(expiryDate.value);
  today.setHours(0, 0, 0, 0);
  expiry.setHours(0, 0, 0, 0);
  const diffTime = expiry.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
});

const calculatePriceRange = computed(() => {
  if (!currentPrice.value || !volatility.value || !daysToExpiry.value) {
    return null;
  }

  const S = parseFloat(currentPrice.value);
  const IV = parseFloat(volatility.value) / 100; // Convert percentage to decimal
  const T = daysToExpiry.value; // Using computed days to expiry
  const sqrtT = Math.sqrt(T / 365);

  // Calculate price range for 68% confidence interval
  const lowerBound = S * Math.exp(-IV * sqrtT);
  const upperBound = S * Math.exp(+IV * sqrtT);

  // Calculate price range for 95% confidence interval
  const lowerBound95 = S * Math.exp(-2 * IV * sqrtT);
  const upperBound95 = S * Math.exp(+2 * IV * sqrtT);

  return {
    confidence68: {
      lower: lowerBound.toFixed(2),
      upper: upperBound.toFixed(2),
    },
    confidence95: {
      lower: lowerBound95.toFixed(2),
      upper: upperBound95.toFixed(2),
    },
  };
});

// Disable dates before today
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7; // 8.64e7 is one day in milliseconds
};

const handleCalculate = () => {
  showResult.value = true;
};

const resetForm = () => {
  currentPrice.value = "";
  volatility.value = "";
  expiryDate.value = "";
  showResult.value = false;
};
</script>

<template>
  <div class="options-calculator">
    <h2>期权价格区间估算</h2>

    <el-form label-width="160px" class="calculator-form">
      <el-form-item label="标的资产当前价格($)">
        <el-input
          v-model="currentPrice"
          type="number"
          placeholder="请输入当前价格"
        />
      </el-form-item>

      <el-form-item label="隐含波动率 (IV)">
        <el-input
          v-model="volatility"
          type="number"
          placeholder="请输入波动率百分比"
        >
          <template #append>%</template>
        </el-input>
      </el-form-item>

      <el-form-item label="到期日期 (T)">
        <el-date-picker
          v-model="expiryDate"
          type="date"
          placeholder="选择到期日期"
          :disabled-date="disabledDate"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
        <span v-if="expiryDate" class="days-display">
          距今 {{ daysToExpiry }} 天
        </span>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleCalculate">计算</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="showResult && calculatePriceRange" class="result-section">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <h3>价格区间预测结果</h3>
            <span class="today-date">当前日期: {{ todayFormatted }}</span>
            <span class="today-date">到期日期: {{ expiryDate }}</span>
          </div>
        </template>

        <div class="confidence-interval">
          <h4>68% 置信区间 (1个标准差):</h4>
          <p>
            价格区间: [{{ calculatePriceRange.confidence68.lower }} -
            {{ calculatePriceRange.confidence68.upper }}]
          </p>
        </div>

        <div class="confidence-interval">
          <h4>95% 置信区间 (2个标准差):</h4>
          <p>
            价格区间: [{{ calculatePriceRange.confidence95.lower }} -
            {{ calculatePriceRange.confidence95.upper }}]
          </p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.options-calculator {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.calculator-form {
  margin-top: 20px;
}

.result-section {
  margin-top: 30px;
}

.result-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.today-date {
  color: #909399;
  font-size: 14px;
}

.confidence-interval {
  margin: 15px 0;
}

.confidence-interval h4 {
  color: #409eff;
  margin-bottom: 10px;
}

h2 {
  color: #303133;
  text-align: center;
}

.days-display {
  margin-left: 10px;
  color: #606266;
}

:deep(.el-date-picker) {
  width: 100%;
}
</style>
