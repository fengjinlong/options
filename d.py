import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import os

# 忽略 pandas 的一些赋值警告，保持输出整洁
pd.options.mode.chained_assignment = None 

# SYMBOL = "KO"
# SYMBOL = "AAPL"
SYMBOL = "NVDA"
# SYMBOL = "TSLA"

HEADERS = {
    "User-Agent": "feng58555@gmail.com"  # 建议使用真实邮箱，避免被 SEC 封禁 IP
}

# SEC API 请求间隔（秒），避免被限流
REQUEST_DELAY = 0.2

# 代理设置（国内用户需要配置）
# PROXY = None  # 例如: "http://127.0.0.1:7890" 或 "http://user:pass@127.0.0.1:7890"
PROXY = "http://127.0.0.1:7890"  # 取消注释并修改为你的代理地址

# 创建带代理的 session
def get_session():
    session = requests.Session()
    if PROXY:
        session.proxies = {
            "http": PROXY,
            "https": PROXY
        }
    return session

SESSION = get_session()

# 是否使用 akshare（国内推荐，stooq 国外需要代理）
USE_AKSHARE = True  # True 使用 akshare，False 使用 stooq

# -----------------------------
# 1. 获取 CIK
# -----------------------------
def get_cik(symbol):
    url = "https://www.sec.gov/files/company_tickers.json"
    print(f"[DEBUG] 请求 CIK API: {url}")
    try:
        response = SESSION.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"[DEBUG] CIK API 响应成功，共 {len(data)} 条记录")
    except requests.exceptions.Timeout:
        print(f"[ERROR] CIK API 请求超时: {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] CIK API HTTP 错误: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] CIK API 请求失败: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] CIK API 解析失败: {e}")
        return None
    
    for k in data:
        if data[k]["ticker"] == symbol:
            cik = str(data[k]["cik_str"]).zfill(10)
            print(f"[DEBUG] 找到 {symbol} 的 CIK: {cik}")
            return cik
    
    print(f"[ERROR] 未找到 symbol: {symbol}")
    return None


# -----------------------------
# 2. 获取 EPS (彻底解决：拆股调整 + 缺失Q4 + 未来函数)
# -----------------------------
def get_eps_history(cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    print(f"[DEBUG] 请求 EPS API: {url}")
    
    try:
        response = SESSION.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()
        print(f"[DEBUG] EPS API 响应成功")
    except requests.exceptions.Timeout:
        print(f"[ERROR] EPS API 请求超时")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] EPS API HTTP 错误: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] EPS API 请求失败: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] EPS API 响应解析失败: {e}")
        return None
    
    try:
        eps = data["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]["USD/shares"]
        print(f"[DEBUG] 获取到 {len(eps)} 条 EPS 原始记录")
    except KeyError as e:
        print(f"[ERROR] EPS 数据结构缺失: {e}")
        print(f"[DEBUG] 可用的 facts keys: {list(data.get('facts', {}).keys())}")
        return None
    except Exception as e:
        print(f"[ERROR] 提取 EPS 数据失败: {e}")
        return None
    
    df = pd.DataFrame(eps)
    
    df = df.dropna(subset=["start", "end", "filed"])
    print(f"[DEBUG] 删除空值后剩余 {len(df)} 条记录")
    
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["filed"] = pd.to_datetime(df["filed"])
    df["days"] = (df["end"] - df["start"]).dt.days
    
    # 【核心1】：先按 filed 排序，确保后续取 last 拿到的是最新的修正/拆股后数值
    df = df.sort_values("filed")
    
    # 【核心2】：提取每个财报期的【最初发布日】(锁定真实历史时间，拒绝穿越)
    first_filed = df.groupby(["end", "days"])["filed"].min().reset_index()
    first_filed.rename(columns={"filed": "original_filed"}, inplace=True)
    
    # 【核心3】：提取每个财报期的【最新 EPS】(获取拆股后的统一比例数值)
    latest_val = df.drop_duplicates(subset=["end", "days"], keep="last")
    
    # 【核心4】：合并清洗，让最新的数值回到真实的历史发布日
    df_clean = pd.merge(latest_val, first_filed, on=["end", "days"])
    df_clean["filed"] = df_clean["original_filed"]
    
    # --- 下面继续使用最稳妥的单季累加法则 ---
    
    # a. 单季数据池
    df_q = df_clean[(df_clean["days"] >= 80) & (df_clean["days"] <= 105)].copy()
    df_q = df_q.drop_duplicates(subset=["end"], keep="last")
    
    # b. 年度数据池
    df_a = df_clean[(df_clean["days"] >= 350) & (df_clean["days"] <= 380)].copy()
    df_a = df_a.drop_duplicates(subset=["end"], keep="last")
    
    # c. 推导缺失的 Q4
    q4_list = []
    for _, a_row in df_a.iterrows():
        fy_end = a_row['end']
        fy_start = fy_end - pd.Timedelta(days=360) 
        
        q_in_fy = df_q[(df_q['end'] > fy_start) & (df_q['end'] < fy_end)]
        
        if len(q_in_fy) == 3 and not (df_q['end'] == fy_end).any():
            q4_eps = a_row['val'] - q_in_fy['val'].sum()
            q4_list.append({
                "date": a_row["filed"], 
                "end_date": fy_end,
                "eps": q4_eps
            })
            
    # 格式化并输出
    df_q["date"] = df_q["filed"]
    df_q["end_date"] = df_q["end"]
    df_q["eps"] = df_q["val"]
    df_q = df_q[["date", "end_date", "eps"]]
    
    if q4_list:
        df_q4 = pd.DataFrame(q4_list)
        df_q = pd.concat([df_q, df_q4], ignore_index=True)
        
    return df_q


# -----------------------------
# 3. 计算 TTM EPS (纯正连续 4 季度滚雪球)
# -----------------------------
def build_ttm_eps(df):
    df = df.sort_values("end_date")
    df["ttm_eps"] = df["eps"].rolling(4).sum()
    df = df.dropna(subset=["ttm_eps"])
    
    # 按照实际发布日对齐
    df = df.sort_values(["date", "end_date"]).reset_index(drop=True)
    return df

# -----------------------------
# 4. 下载近一年股价
# -----------------------------
def get_price(symbol):
    one_year = datetime.now() - timedelta(days=365)
    
    if USE_AKSHARE:
        print(f"[DEBUG] 使用 akshare 获取 {symbol} 股价...")
        try:
            import akshare as ak
            df = ak.stock_us_daily(symbol=symbol)
            df["Date"] = pd.to_datetime(df["date"])
            df = df.rename(columns={"close": "Close"})
            df = df[df["Date"] >= one_year].copy()
            df = df.sort_values("Date")
            print(f"[DEBUG] akshare 返回 {len(df)} 条记录")
            return df[["Date", "Close"]]
        except ImportError:
            print(f"[ERROR] 请先安装 akshare: pip install akshare")
            return None
        except Exception as e:
            print(f"[ERROR] akshare 获取股价失败: {e}")
            return None
    else:
        # 使用 stooq（需要代理）
        url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d"
        print(f"[DEBUG] 请求股价 API: {url}")
        try:
            df = pd.read_csv(url)
            print(f"[DEBUG] 股价 API 响应成功，共 {len(df)} 条记录")
        except Exception as e:
            print(f"[ERROR] 股价 API 请求/解析失败: {e}")
            return None
        
        if df.empty:
            print(f"[ERROR] 股价数据为空")
            return None
        
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        
        df = df[df["Date"] >= one_year].copy()
        print(f"[DEBUG] 筛选近一年数据后剩余 {len(df)} 条记录")
        
        return df


# -----------------------------
# 5. 计算每日 PE
# -----------------------------
def calculate_pe(price_df, eps_df):
    pe_list = []
    for _, row in price_df.iterrows():
        date = row["Date"]
        price = row["Close"]
        
        # 寻找在该交易日及之前已经发布的最新财报
        eps_valid = eps_df[eps_df["date"] <= date]
        
        if len(eps_valid) == 0:
            pe_list.append(None)
            continue
            
        ttm_eps = eps_valid.iloc[-1]["ttm_eps"]
        
        if ttm_eps <= 0:
            pe_list.append(None)
        else:
            pe_list.append(price / ttm_eps)
            
    price_df["PE"] = pe_list
    return price_df.dropna()


# -----------------------------
# 6. 画图展示 (已进行视觉优化)
# -----------------------------
def plot_pe(df):
    plt.figure(figsize=(10, 5))
    
    # 基础 PE 线
    plt.plot(df["Date"], df["PE"], label="Daily PE", color="#1f77b4", linewidth=1.5)
    
    # 计算关键位
    p20 = df["PE"].quantile(0.2)
    p80 = df["PE"].quantile(0.8)
    current_pe = df["PE"].iloc[-1]
    
    # 画分位线
    plt.axhline(p20, linestyle="--", color="green", alpha=0.8, label=f"20% Percentile ({p20:.2f})")
    plt.axhline(p80, linestyle="--", color="orange", alpha=0.8, label=f"80% Percentile ({p80:.2f})")
    
    # 高亮当前 PE
    plt.axhline(current_pe, linestyle="-", color="red", linewidth=2, label=f"Current PE ({current_pe:.2f})")
    
    # 填充 20-80 的正常估值区间
    plt.fill_between(df["Date"], p20, p80, color="gray", alpha=0.15)
    
    plt.title(f"{SYMBOL} Daily PE (Trailing 1 Year)")
    plt.xlabel("Date")
    plt.ylabel("P/E Ratio")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


# -----------------------------
# 主程序
# -----------------------------
def main():
    print("======== PE Analysis ========")
    
    cik = get_cik(SYMBOL)
    if cik is None:
        print("[ERROR] 无法获取 CIK，程序终止")
        return
    
    time.sleep(REQUEST_DELAY)  # 避免请求过快被限流
    
    eps = get_eps_history(cik)
    if eps is None or eps.empty:
        print("[ERROR] 无法获取 EPS 数据，程序终止")
        return
    
    eps = build_ttm_eps(eps)
    
    if eps.empty:
        print("[ERROR] TTM EPS 计算结果为空")
        return
    
    # 打印检查最近 8 个季度，确认 Q4 是否成功补全、时序是否正确
    print("\n--- TTM EPS Check (Last 8 Quarters) ---")
    print(eps.tail(8).to_string(index=False))
    print("---------------------------------------\n")
    
    price = get_price(SYMBOL)
    if price is None or price.empty:
        print("[ERROR] 无法获取股价数据，程序终止")
        return
    
    result = calculate_pe(price, eps)
    
    if result.empty:
        print("[ERROR] 无法计算 PE，可能缺少有效数据。")
        print(f"[DEBUG] price 数据: {len(price)} 行")
        print(f"[DEBUG] eps 数据: {len(eps)} 行")
        return

    current_pe = result["PE"].iloc[-1]
    percentile = (result["PE"] < current_pe).mean() * 100
    
    print(f"Symbol: {SYMBOL}")
    print(f"Current PE: {current_pe:.2f}")
    print(f"1Y Percentile: {percentile:.2f} %")
    print("------------------------------")
    print(result[["Date", "Close", "PE"]].tail())
    
    plot_pe(result)


if __name__ == "__main__":
    main()