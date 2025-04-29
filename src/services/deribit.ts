import axios from "axios";

const BASE_URL = "https://www.deribit.com/api/v2";

// Interface for API response
interface VolatilityResponse {
  jsonrpc: string;
  result: Array<[number, number]>; // [timestamp, value]
  testnet: boolean;
  usDiff: number;
  usIn: number;
  usOut: number;
}

// Interface for formatted data
export interface VolatilityData {
  timestamp: string;
  value: number;
}

export const fetchHistoricalVolatility = async (
  currency: string,
  resolution: string = "1D"
): Promise<VolatilityData[]> => {
  try {
    const response = await axios.get<VolatilityResponse>(
      `${BASE_URL}/public/get_historical_volatility`,
      {
        params: {
          currency,
          resolution,
        },
      }
    );

    // Log the first few values to debug
    console.log(
      `First few values for ${currency}:`,
      response.data.result.slice(0, 3)
    );

    return response.data.result.map(([timestamp, value]) => ({
      timestamp: new Date(timestamp).toISOString(),
      value: Number(value.toFixed(2)), // Keep the original value as it's already a percentage
    }));
  } catch (error) {
    console.error(`Error fetching ${currency} volatility:`, error);
    throw error;
  }
};
