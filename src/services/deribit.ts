import axios from "axios";

const BASE_URL = "https://test.deribit.com/api/v2";

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

interface DvolResponse {
  jsonrpc: string;
  result: {
    data: Array<{
      date: string;
      delivery_price: number;
    }>;
  };
  usIn: number;
  usOut: number;
  usDiff: number;
}

export async function getDvolData(
  symbol: string,
  offset: number,
  count: number = 100
) {
  try {
    const response = await axios.get<DvolResponse>(
      `${BASE_URL}/public/get_delivery_prices`,
      {
        params: {
          offset,
          count,
          index_name: `${symbol.toLowerCase()}dvol_usdc`,
        },
      }
    );

    return response.data.result.data.map((item) => ({
      date: item.date,
      dvol: Number(item.delivery_price.toFixed(2)), // Just keep 2 decimal places
    }));
  } catch (error) {
    console.error(`Error fetching DVOL data for ${symbol}:`, error);
    throw error;
  }
}

export async function getFullYearDvol(symbol: string) {
  const TOTAL_DAYS = 365;
  const PAGE_SIZE = 100;
  const pages = Math.ceil(TOTAL_DAYS / PAGE_SIZE);
  const promises = [];

  for (let i = 0; i < pages; i++) {
    const offset = i * PAGE_SIZE;
    const count = Math.min(PAGE_SIZE, TOTAL_DAYS - offset);
    promises.push(getDvolData(symbol, offset, count));
  }

  try {
    const results = await Promise.all(promises);
    const data = results
      .flat()
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    // Log the processed data for debugging
    console.log(`Processed ${symbol} DVOL data:`, data);
    return data;
  } catch (error) {
    console.error(`Error fetching full year DVOL data for ${symbol}:`, error);
    throw error;
  }
}

interface IndexPriceResponse {
  jsonrpc: string;
  result: {
    index_price: number;
  };
  testnet: boolean;
  usIn: number;
  usOut: number;
  usDiff: number;
}

export const fetchCurrentDvol = async (currency: string): Promise<number> => {
  try {
    const response = await axios.get<IndexPriceResponse>(
      `${BASE_URL}/public/get_index_price`,
      {
        params: {
          index_name: `${currency.toLowerCase()}dvol_usdc`,
        },
      }
    );

    return Number(response.data.result.index_price.toFixed(2));
  } catch (error) {
    console.error(`Error fetching current DVOL for ${currency}:`, error);
    throw error;
  }
};
