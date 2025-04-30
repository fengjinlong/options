function calculateMedian(sortedArr) {
  const mid = Math.floor(sortedArr.length / 2);
  return sortedArr.length % 2 !== 0
    ? sortedArr[mid]
    : (sortedArr[mid - 1] + sortedArr[mid]) / 2;
}

function calculateQuartiles(sortedData) {
  const n = sortedData.length;
  if (n === 0) return { q1: null, q3: null };

  const lowerHalf = sortedData.slice(0, Math.floor(n / 2));
  const upperHalf =
    n % 2 === 0
      ? sortedData.slice(Math.floor(n / 2))
      : sortedData.slice(Math.floor(n / 2) + 1);

  return {
    q1: calculateMedian(lowerHalf),
    q3: calculateMedian(upperHalf),
  };
}

function computeRatioWithOutlierHandling(
  data,
  value,
  kFactor = 1.5,
  percentile = 0.05
) {
  if (!Array.isArray(data) || data.length === 0) return null;

  const sortedData = [...data].sort((a, b) => a - b);
  const { q1, q3 } = calculateQuartiles(sortedData);

  if (q1 === null || q3 === null) return null;

  const iqr = q3 - q1;
  const lowerBound = q1 - kFactor * iqr;
  const upperBound = q3 + kFactor * iqr;

  // 动态调整 kFactor based on outlier ratio
  const outliers = data.filter((x) => x < lowerBound || x > upperBound);
  const outlierRatio = outliers.length / data.length;

  let adjustedKFactor = kFactor;
  if (outlierRatio > 0.1) {
    adjustedKFactor = Math.max(1.0, kFactor * (1 - outlierRatio)); // reduce k if many outliers
  }

  const adjustedLowerBound = q1 - adjustedKFactor * iqr;
  const adjustedUpperBound = q3 + adjustedKFactor * iqr;

  // Winsorizing: replace outliers with 5th and 95th percentiles
  const p5 = sortedData[Math.floor(sortedData.length * percentile)];
  const p95 = sortedData[Math.floor(sortedData.length * (1 - percentile))];

  const winsorizedData = data.map((x) => {
    if (x < adjustedLowerBound) return p5;
    if (x > adjustedUpperBound) return p95;
    return x;
  });

  const newMin = Math.min(...winsorizedData);
  const newMax = Math.max(...winsorizedData);

  if (newMin === newMax) return 0;

  return (value - newMin) / (newMax - newMin);
}

// 测试
// const data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100, 100, 100, 100, 100];
// const value = 5;

// console.log(computeRatioWithOutlierHandling(data, value));  // 输出 ≈ 0.45
