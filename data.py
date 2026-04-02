import requests
from datetime import datetime, timedelta

def get_nvda_data(api_key):
    symbol = "NVDA"
    base_url = "https://www.alphavantage.co/query"
    
    # 计算一年前的日期，用于过滤数据
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"开始通过 Alpha Vantage 获取 {symbol} 的数据...")

    # ==========================================
    # 1. 获取过去一年的每日收盘价
    # ==========================================
    # 注意：必须使用 outputsize=full 才能获取超过 100 天的数据
    price_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key
    }
    
    price_response = requests.get(base_url, params=price_params)
    price_data = price_response.json()
    
    daily_close_dict = {}
    time_series = price_data.get("Time Series (Daily)", {})
    
    if not time_series:
        print("获取价格数据失败，请检查 API Key 或调用频率限制。")
        print(price_data)
    else:
        # 遍历数据，只保留最近一年的收盘价
        for date_str, metrics in time_series.items():
            if date_str >= one_year_ago:
                # 提取 "4. close" 字段并转换为浮点数
                daily_close_dict[date_str] = float(metrics["4. close"])

    # ==========================================
    # 2. 获取季度 EPS (每股收益) 数据
    # ==========================================
    earnings_params = {
        "function": "EARNINGS",
        "symbol": symbol,
        "apikey": api_key
    }
    
    earnings_response = requests.get(base_url, params=earnings_params)
    earnings_data = earnings_response.json()
    
    quarterly_eps_dict = {}
    quarterly_earnings = earnings_data.get("quarterlyEarnings", [])
    
    if not quarterly_earnings:
        print("获取 EPS 数据失败，请检查 API Key 或调用频率限制。")
        print(earnings_data)
    else:
        # 遍历财务数据，提取财报发布日期和对应的实际 EPS
        # 通常我们只需要最近几个季度的数据（例如最近 4 到 8 个季度）
        for quarter in quarterly_earnings[:8]: 
            # reportedDate 是财报实际发布日期
            report_date = quarter.get("reportedDate")
            actual_eps = quarter.get("reportedEPS")
            
            if report_date and actual_eps and actual_eps != "None":
                quarterly_eps_dict[report_date] = float(actual_eps)

    # ==========================================
    # 3. 组装并返回结构化数据
    # ==========================================
    result = {
        "symbol": symbol,
        "date_range": f"{one_year_ago} to present",
        "daily_prices": daily_close_dict,
        "quarterly_eps": quarterly_eps_dict
    }
    
    return result

if __name__ == "__main__":
    # 替换为你自己的 Alpha Vantage API Key
    ALPHA_VANTAGE_API_KEY = "F0IC02DDG76QYI23"
    
    nvda_data = get_nvda_data(ALPHA_VANTAGE_API_KEY)
    
    # 打印结果看看结构 (只打印前几个价格数据防止刷屏)
    print("\n--- 数据获取完成 ---")
    print(f"股票代码: {nvda_data['symbol']}")
    print(f"共获取到 {len(nvda_data['daily_prices'])} 天的有效收盘价。")
    print(f"共获取到 {len(nvda_data['quarterly_eps'])} 个季度的 EPS 数据。")
    
    print("\n季度 EPS 样本:")
    for date, eps in nvda_data['quarterly_eps'].items():
        print(f"  {date}: {eps}")