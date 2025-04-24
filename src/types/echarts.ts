// ECharts tooltip formatter parameter types
export interface EChartsTooltipFormatterParams {
  dataIndex: number;
  seriesName?: string;
  value?: number | string | (number | string)[];
  data?: any;
  color?: string;
  axisValue?: string;
  // Add more properties as needed
}

// Volatility data point type
export interface VolatilityDataPoint {
  date: string;
  value: number;
  price: number;
}
