import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import pytz
import warnings
import gc
import json
import os
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

# ==========================================
# 0. MESIN REAKTIF & CACHE PERSISTEN (V17.9.8)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v1798.json"

def load_reactive_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
            loaded_stocks = cache_data.get("raw_stocks", [])
            ihsg_data = cache_data.get("ihsg", {"val": 0, "change": 0})
            if loaded_stocks and isinstance(loaded_stocks, list):
                return loaded_stocks, cache_data.get("last_update", None), ihsg_data
        except:
            pass
    return [], None, {"val": 0, "change": 0}

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update, st.session_state.ihsg_data = load_reactive_cache()
if "reactive_mode" not in st.session_state:
    st.session_state.reactive_mode = False
if "current_tf" not in st.session_state:
    st.session_state.current_tf = "1 Hari (Harian)"

# ==========================================
# 1. UI MEWAH & CSS MOBILE EKSTREM
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v17.9.8", page_icon="✨", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: #050505 !important; color: #A1A1AA !important; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 3.5rem !important; padding-bottom: 1rem !important; max-width: 100% !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
section[data-testid="stSidebar"] { background-color: #09090B !important; border-right: 1px solid #1F1F22 !important; min-width: 180px !important; max-width: 180px !important; }
section[data-testid="stSidebar"] * { color: #A1A1AA !important; }
div[data-baseweb="select"] > div { background-color: #09090B !important; border: 1px solid #27272A !important; border-radius: 8px !important; padding: 4px !important; }
div[data-baseweb="select"] span { color: #FAFAFA !important; font-weight: 600 !important; font-size: 14px !important; }
.pro-card { background: linear-gradient(145deg, #121214, #09090B); border: 1px solid #27272A; border-radius: 10px; padding: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 10px; }
.market-banner { background: linear-gradient(145deg, #18181B, #09090B); border: 1px solid #3F3F46; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
.card-label { color: #C6A87C; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 6px;}
.header-profile { display: flex; justify-content: space-between; align-items: center; }
.ticker-title { font-size: 24px; font-weight: 800; color: #FAFAFA; line-height: 1.1; display: flex; align-items: center; gap: 6px;}
.ticker-desc { color: #A1A1AA; font-size: 12px; font-weight: 500; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px;}
.badge-primary { background: rgba(198, 168, 124, 0.1); color: #C6A87C; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(198, 168, 124, 0.3);}
.badge-green { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
.badge-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
.badge-blue { background: rgba(59, 130, 246, 0.1); color: #3B82F6; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.3);}
.score-box { background: #050505; border: 1px solid #27272A; border-radius: 8px; padding: 10px 14px; text-align: center; }
.score-value { font-size: 32px; font-weight: 800; color: #C6A87C; line-height: 1; margin: 4px 0;}
.data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;}
.data-label { font-size: 10px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; display: block;}
.data-value { font-size: 14px; color: #FAFAFA; font-weight: 700; display: block;}
.meter-container { background: #27272A; height: 6px; border-radius: 3px; margin-top: 15px; position: relative;}
.meter-fill { background: linear-gradient(90deg, #EF4444 0%, #C6A87C 50%, #10B981 100%); height: 100%; border-radius: 3px;}
.meter-labels { display: flex; justify-content: space-between; font-size: 10px; color: #71717A; font-weight: 600; margin-top: 4px;}
.stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 0px;}
.stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 600; background: transparent; padding: 8px 6px; border: none; font-size: 12px;}
.stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
.sop-box { background: #09090B; border-left: 3px solid #C6A87C; padding: 12px; margin-bottom: 15px; font-size: 12px; color: #D4D4D8; line-height:1.6;}
.sop-title { color: #C6A87C; font-weight: 700; font-size: 14px; margin-bottom: 8px; text-transform: uppercase;}
div[data-baseweb="input"] { background-color: #050505 !important; border: 1px solid #27272A !important; border-radius: 6px !important; }
div[data-baseweb="input"] input { color: #FAFAFA !important; font-size: 13px !important; }
@media (max-width: 768px) {
    .ticker-title { font-size: 18px; }
    .ticker-desc { font-size: 11px; max-width: 140px; white-space: normal; line-height: 1.2; }
    .score-box { padding: 6px 10px; }
    .score-value { font-size: 24px; }
    .data-grid { grid-template-columns: 1fr 1fr !important; }
    .market-banner { flex-direction: column; text-align: center; gap: 6px; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PENGAMBILAN DATA MESIN INTI & INDIKATOR
# ==========================================
MASTER_UNIVERSE = [
    "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT",
    "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM",
    "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR",
    "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR",
    "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS",
    "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP",
    "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE",
    "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH",
    "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA",
    "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS",
    "BBYB", "AGRO", "ARKA", "TOTO", "MLBI", "INDY", "PTRO", "MBAP", "BSSR", "SMMT",
    "KKGI", "ABMM", "CFIN", "MFIN", "ADMF", "BBKP", "PNBN", "BNLI", "SAGE", "GZCO",
    "STRK", "WIFI", "AEGS", "GOLF", "FILM", "ELSA", "RAJA", "HATM", "KRYA", "BSBK",
    "DATA", "NICL", "PAMG", "TRJA", "CARS", "BAPA", "KIJA", "DILD", "LPCK"
]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib():
    return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M")

def fetch_ihsg():
    try:
        tkr = yf.Ticker("^JKSE")
        hist = tkr.history(period="5d")
        if len(hist) >= 2:
            sekarang = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            perubahan = ((sekarang - prev) / prev) * 100
            return {"val": sekarang, "change": perubahan}
    except:
        pass
    return {"val": 0, "change": 0}

def get_dynamic_market_roster():
    try:
        df_batch = yf.download(master_tickers, period="5d", group_by="ticker", threads=True, progress=False)
        market_data = []
        for ticker in master_tickers:
            try:
                if isinstance(df_batch.columns, pd.MultiIndex):
                    df_t = df_batch[ticker].dropna()
                else:
                    df_t = df_batch.dropna()
                if len(df_t) < 2:
                    continue
                
                close_now = float(df_t['Close'].iloc[-1])
                close_prev = float(df_t['Close'].iloc[-2])
                vol_now = float(df_t['Volume'].iloc[-1])
                
                if close_now < 50 or vol_now < 50000:
                    continue
                    
                pct_change = ((close_now - close_prev) / close_prev) * 100
                trans_val = close_now * vol_now
                market_data.append({'Ticker': ticker, 'Change': pct_change, 'TransVal': trans_val, 'VolatilityScore': abs(pct_change) * trans_val})
            except:
                continue
                
        df_market = pd.DataFrame(market_data)
        if df_market.empty:
            return master_tickers[:300]
            
        top_gainers = df_market.nlargest(100, 'Change')['Ticker'].tolist()
        top_liquid = df_market.nlargest(100, 'TransVal')['Ticker'].tolist()
        top_volatile = df_market.nlargest(100, 'VolatilityScore')['Ticker'].tolist()
        return list(set(top_gainers + top_liquid + top_volatile))[:300]
    except:
        return master_tickers[:300]

@st.cache_data(ttl=3600)
def fetch_quarterly_financials(ticker):
    try:
        tkr = yf.Ticker(ticker)
        inc_stmt = tkr.quarterly_income_stmt
        if inc_stmt is None or inc_stmt.empty:
            inc_stmt = tkr.quarterly_financials
            
        cf_stmt = tkr.quarterly_cash_flow
        if cf_stmt is None or cf_stmt.empty:
            cf_stmt = tkr.quarterly_cashflow
            
        net_income_series = None
        if inc_stmt is not None and not inc_stmt.empty:
            for idx in inc_stmt.index:
                if 'net income' in str(idx).lower() and 'continuous' not in str(idx).lower():
                    net_income_series = inc_stmt.loc[idx]
                    break
            if net_income_series is None and "Net Income" in inc_stmt.index:
                net_income_series = inc_stmt.loc["Net Income"]
                
        op_cf_series = None
        if cf_stmt is not None and not cf_stmt.empty:
            for idx in cf_stmt.index:
                if 'operating cash flow' in str(idx).lower() or 'total cash from operating activities' in str(idx).lower():
                    op_cf_series = cf_stmt.loc[idx]
                    break
            if op_cf_series is None and "Operating Cash Flow" in cf_stmt.index:
                op_cf_series = cf_stmt.loc["Operating Cash Flow"]
                
        if net_income_series is None and op_cf_series is None:
            return None
            
        tanggal = []
        if net_income_series is not None:
            tanggal.extend(list(net_income_series.index))
        if op_cf_series is not None:
            tanggal.extend(list(op_cf_series.index))
            
        tanggal = sorted(list(set(tanggal)))
        data = {'Tanggal': tanggal, 'Laba Bersih': [], 'Arus Kas Operasional': []}
        
        for d in tanggal:
            ni_val = net_income_series.get(d, 0) if net_income_series is not None else 0
            cf_val = op_cf_series.get(d, 0) if op_cf_series is not None else 0
            data['Laba Bersih'].append(ni_val if not pd.isna(ni_val) else 0)
            data['Arus Kas Operasional'].append(cf_val if not pd.isna(cf_val) else 0)
            
        df_chart = pd.DataFrame(data)
        df_chart['Tanggal'] = pd.to_datetime(df_chart['Tanggal'])
        df_chart = df_chart.sort_values('Tanggal', ascending=True)
        df_chart['Quarter'] = df_chart['Tanggal'].dt.to_period('Q').astype(str)
        return df_chart
    except:
        return None

def format_rupiah_short(val):
    if val == 0 or pd.isna(val):
        return "-"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e12:
        return f"{sign}{abs_val/1e12:.1f}T"
    elif abs_val >= 1e9:
        return f"{sign}{abs_val/1e9:.1f}B"
    elif abs_val >= 1e6:
        return f"{sign}{abs_val/1e6:.1f}M"
    else:
        return f"{sign}{abs_val:,.0f}"

def hitung_rsi(df, periods=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/periods, min_periods=periods).mean()
    loss = (-1 * delta.clip(upper=0)).ewm(alpha=1/periods, min_periods=periods).mean()
    return 100 - (100 / (1 + (gain / loss)))

def hitung_stochastic(df, k_period=14, d_period=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min + 1e-9))
    return stoch_k, stoch_k.rolling(window=d_period).mean()

def check_bullish_divergence(df, window=20):
    try:
        recent = df.tail(window)
        if len(recent) < window:
            return False
        p_min1_idx = recent['Low'].iloc[:-5].idxmin()
        p_min2_idx = recent['Low'].iloc[-5:].idxmin()
        if (recent.loc[p_min2_idx, 'Low'] < recent.loc[p_min1_idx, 'Low']) and (recent.loc[p_min2_idx, 'RSI'] > recent.loc[p_min1_idx, 'RSI']):
            return True
    except:
        pass
    return False

def hitung_atr(df, periode=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    return np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1).rolling(periode).mean()

def fetch_single_stock(emiten, mode_tf):
    try:
        per, inv = "1y", "1d"
        kode = emiten.replace(".JK", "")
        tkr = yf.Ticker(emiten)
        df = tkr.history(period=per, interval=inv)
        if df.empty:
            return None
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        df = df.ffill().dropna(subset=['Close'])
        
        if len(df) < 30:
            return None
            
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = hitung_rsi(df)
        df['Stoch_K'], df['Stoch_D'] = hitung_stochastic(df)
        df['ATR'] = hitung_atr(df)
        df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Chandelier_Exit'] = df['High'].rolling(22).max() - (df['ATR'] * 3.0)
        
        harga_tipikal = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (harga_tipikal * df['Volume']).rolling(window=20).sum() / df['Volume'].rolling(window=20).sum()
        vwap_skg = float(df['VWAP'].iloc[-1]) if not pd.isna(df['VWAP'].iloc[-1]) else float(df['Close'].iloc[-1])
        
        fibo_window = df.tail(120)
        max_h = float(fibo_window['High'].max())
        min_l = float(fibo_window['Low'].min())
        fibo_diff = max_h - min_l
        fibo_236 = max_h - 0.236 * fibo_diff
        fibo_382 = max_h - 0.382 * fibo_diff
        fibo_500 = max_h - 0.500 * fibo_diff
        fibo_618 = max_h - 0.618 * fibo_diff
        
        df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        macd_val = float(df['MACD'].iloc[-1])
        sig_val = float(df['Signal_Line'].iloc[-1])
        macd_bullish = macd_val > sig_val
        
        harga_skg = float(df['Close'].iloc[-1])
        open_skg = float(df['Open'].iloc[-1])
        high_skg = float(df['High'].iloc[-1])
        low_skg = float(df['Low'].iloc[-1])
        vol_skg = float(df['Volume'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        ema20_skg = float(df['EMA20'].iloc[-1])
        sma50_skg = float(df['SMA50'].iloc[-1])
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        low_20 = float(df['Low'].tail(20).min())
        
        is_near_bottom = (harga_skg - low_20) / low_20 <= 0.06
        has_bullish_div = check_bullish_divergence(df, window=20)
        is_bullish = harga_skg >= open_skg
        body_size = abs(open_skg - harga_skg)
        lower_shadow = (open_skg if is_bullish else harga_skg) - low_skg
        
        is_whale_absorption = (vol_skg > vol_sma20 * 1.3) and (lower_shadow > body_size * 1.5) and is_near_bottom
        
        if has_bullish_div and is_near_bottom:
            serok_signal = "🎯 DIVERGENSI BULLISH"
        elif is_whale_absorption:
            serok_signal = "🐳 PENYERAPAN PAUS"
        elif (float(df['Stoch_K'].iloc[-1]) < 30) and (float(df['Stoch_K'].iloc[-1]) > float(df['Stoch_D'].iloc[-1])) and is_near_bottom:
            serok_signal = "🟢 OVERSOLD REBOUND"
        else:
            serok_signal = "➖ TDK ADA"
            
        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg:
            trailing_stop = harga_skg - (float(df['ATR'].iloc[-1]) * 2)
            
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        is_vol_spike = vol_skg > (vol_sma20 * 1.2)
        
        if is_vol_spike:
            if lower_shadow > (body_size * 1.5):
                status_bandar = "🐳 AKUMULASI BAWAH"
            elif upper_shadow > (body_size * 1.5):
                status_bandar = "🩸 DISTRIBUSI PUCUK"
            elif is_bullish and wpi_score > 70:
                status_bandar = "🚀 MARK-UP BERINGAS"
            elif is_bullish:
                status_bandar = "🟢 AKUMULASI AWAL"
            else:
                status_bandar = "💥 MARK-DOWN"
        else:
            status_bandar = "➖ NETRAL"
            
        setup_score = sum([harga_skg > ema20_skg, wpi_score > 85, vol_skg > vol_sma20*2, "TDK ADA" not in serok_signal, macd_bullish])
        
        if "TDK ADA" not in serok_signal:
            setup_grade = "🎯 SETUP JACKPOT"
        elif setup_score >= 3 and wpi_score >= 70:
            setup_grade = "⭐ SETUP A+"
        elif setup_score >= 2 and wpi_score >= 80:
            setup_grade = "⚡ SETUP AGRESIF"
        elif setup_score >= 1:
            setup_grade = "✔️ SETUP B"
        else:
            setup_grade = "⚠️ WAIT/WATCHLIST"
            
        info = tkr.info if hasattr(tkr, 'info') and tkr.info else {}
        sector_val = info.get('sector', 'Sektor Tidak Tersedia')
        industry_val = info.get('industry', 'Industri Tidak Tersedia')
        
        div_rate = info.get('dividendRate', 0)
        raw_yield = info.get('dividendYield', 0)
        
        if div_rate and div_rate > 0 and harga_skg > 0:
            div_yield = (div_rate / harga_skg) * 100
        else:
            div_yield = (raw_yield * 100) if (raw_yield and raw_yield < 1) else (raw_yield if raw_yield else 0.0)
        div_yield = round(div_yield, 2)
        
        roe_raw = info.get('returnOnEquity', 0)
        roe_pct = round(roe_raw * 100, 2) if roe_raw else 0.0
        
        per_val = info.get('trailingPE', 0.0)
        pbv_val = info.get('priceToBook', 0)
        
        if pbv_val and pbv_val > 100:
            if per_val and roe_raw:
                pbv_val = per_val * roe_raw
            else:
                pbv_val = pbv_val / 16000
        pbv_val = round(pbv_val, 2) if pbv_val else 0.0
        eps_val = float(info.get('trailingEps', 0.0))
        
        target_low = info.get('targetLowPrice', 0)
        target_mean = info.get('targetMeanPrice', 0)
        target_high = info.get('targetHighPrice', 0)
        rec_key = str(info.get('recommendationKey', 'none')).replace('_', ' ').upper()
        num_analysts = info.get('numberOfAnalystOpinions', 0)
        
        bid_price = info.get('bid', 0)
        ask_price = info.get('ask', 0)
        bid_size = info.get('bidSize', 0)
        ask_size = info.get('askSize', 0)
        
        return {
            "TICKER": kode,
            "HARGA": harga_skg,
            "MA20": ema20_skg,
            "MA50": sma50_skg,
            "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3),
            "TRAILING STOP": trailing_stop,
            "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal,
            "STATUS_BANDAR": status_bandar,
            "SETUP_GRADE": setup_grade,
            "PER": round(per_val, 2) if per_val else 0.0,
            "ROE": roe_pct,
            "YIELD": f"{div_yield}%",
            "YIELD_RAW": div_yield,
            "PBV": pbv_val,
            "EPS": eps_val,
            "RET_1D": ((harga_skg - prev_close) / prev_close * 100),
            "VOLUME": vol_skg,
            "VOL_SMA20": vol_sma20,
            "ATR_PCT": (float(df['ATR'].iloc[-1]) / harga_skg) * 100,
            "NAME": info.get('longName', kode),
            "SECTOR": sector_val,
            "INDUSTRY": industry_val,
            "MACD_BULLISH": macd_bullish,
            "TARGET_LOW": target_low,
            "TARGET_MEAN": target_mean,
            "TARGET_HIGH": target_high,
            "REC_KEY": rec_key,
            "JUMLAH_ANALIS": num_analysts,
            "VWAP": vwap_skg,
            "FIBO_236": fibo_236,
            "FIBO_382": fibo_382,
            "FIBO_500": fibo_500,
            "FIBO_618": fibo_618,
            "FIBO_MAX": max_h,
            "FIBO_MIN": min_l,
            "BID": bid_price,
            "ASK": ask_price,
            "UKURAN_PENAWARAN": bid_size,
            "UKURAN_TANYA": ask_size
        }
    except Exception as e:
        return None

# ==========================================
# 3. SIDEBAR (KEMEWAHAN ULTRA-SEMPIT)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#C6A87C; font-size:16px; font-weight:800; margin-bottom:0;'>✨ JG ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#71717A; font-size:9px; letter-spacing:1px; margin-bottom:20px;'>EDISI V17.9.8</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:10px; color:#A1A1AA; margin-bottom:5px;'>⏱️ Jangka Waktu:</div>", unsafe_allow_html=True)
    tf_pilihan = st.selectbox("TF", ("1 Hari (Harian)", "1 Minggu (Mingguan)"), index=0, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='color:#FAFAFA; font-size:10px; font-weight:700; margin-bottom:5px;'>⚙️ AUTO-SYNC</div>", unsafe_allow_html=True)
    
    reactive_on = st.toggle("Mode Langsung", value=st.session_state.reactive_mode)
    if reactive_on != st.session_state.reactive_mode:
        st.session_state.reactive_mode = reactive_on
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 SCAN", use_container_width=True):
        st.session_state.raw_stocks = []
        
        radar_bar_ihsg = st.progress(0, text="Mengambil data IHSG...")
        st.session_state.ihsg_data = fetch_ihsg()
        radar_bar_ihsg.empty()
        
        radar_bar = st.progress(0, text="Mendeteksi Saham Aktif...")
        dynamic_tickers = get_dynamic_market_roster()
        radar_bar.empty()
        
        my_bar = st.progress(0, text=f"Memindai...")
        for i, t in enumerate(dynamic_tickers):
            my_bar.progress((i + 1) / len(dynamic_tickers), text=f"{t} ({i+1}/{len(dynamic_tickers)})")
            data = fetch_single_stock(t, tf_pilihan)
            if data:
                st.session_state.raw_stocks.append(data)
            gc.collect()
        my_bar.empty()
        
        st.session_state.last_update = get_waktu_wib()
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update, "ihsg": st.session_state.ihsg_data}, f)
        except:
            pass
        st.rerun()
        
    if st.session_state.last_update:
        st.markdown(f"<div style='font-size:8px; color:#71717A; text-align:center; margin-top:20px;'>Pembaruan Terakhir:<br>{st.session_state.last_update}</div>", unsafe_allow_html=True)

# ==========================================
# 4. TAB UTAMA
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN' di sidebar untuk memulai.")
else:
    tab_dash, tab_cluster, tab_export, tab_sop = st.tabs(["✨ DASHBOARD", "🎯 CLUSTER", "📥 EXPORT", "📖 SOP"])

    # ------------------------------------------
    # TAB 1: DASHBOARD MEWAH
    # ------------------------------------------
    with tab_dash:
        last_up_text = st.session_state.last_update if st.session_state.last_update else "Belum diset"
        ihsg = st.session_state.ihsg_data
        ihsg_val = ihsg.get("val", 0)
        ihsg_change = ihsg.get("change", 0)
        
        ihsg_color = "#10B981" if ihsg_change >= 0 else "#EF4444"
        ihsg_sign = "+" if ihsg_change >= 0 else ""
        
        market_banner_html = f"""
        <div class="market-banner">
            <div>
                <div style="font-size:10px; color:#A1A1AA; text-transform:uppercase; letter-spacing:1px; font-weight:700;">🇮🇩 IHSG (KOMPOSIT)</div>
                <div style="font-size:18px; font-weight:800; color:{ihsg_color}; margin-top:2px;">{ihsg_val:,.2f} <span style="font-size:12px; font-weight:600;">({ihsg_sign}{ihsg_change:.2f}%)</span></div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; color:#71717A;">Status Sinkronisasi</div>
                <div style="font-size:11px; font-weight:700; color:#C6A87C;">{last_up_text}</div>
            </div>
        </div>
        """
        st.markdown(market_banner_html, unsafe_allow_html=True)
        
        st.markdown("<div style='font-size:11px; color:#71717A; font-weight:700; margin-bottom:5px; text-transform:uppercase;'>🔍 Cari Emiten</div>", unsafe_allow_html=True)
        pilihan_ticker = st.selectbox("Pilih", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0, label_visibility="collapsed")
        
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            grade = s.get("SETUP_GRADE", "WAIT")
            atr_pct = s.get('ATR_PCT', 0)
            volatility_badge = "TINGGI" if atr_pct > 4 else "NORMAL"
            
            if "JACKPOT" in grade or "A+" in grade:
                action_text, action_color, action_bg = "BELI / AKUMULASIKAN", "#10B981", "rgba(16, 185, 129, 0.1)"
            elif "WAIT" in grade:
                action_text, action_color, action_bg = "TUNGGU / DAFTAR PANTAU", "#C6A87C", "rgba(198, 168, 124, 0.1)"
            else:
                action_text, action_color, action_bg = "BELI SPEKULATIF", "#FAFAFA", "rgba(250, 250, 250, 0.1)"
                
            vol = s.get('VOLUME', 0)
            vol_sma = s.get('VOL_SMA20', 1)
            status_bandar = s.get('STATUS_BANDAR', 'NETRAL')
            serok_sig = s.get('SEROK_SIGNAL', '➖ TDK ADA').split()[0]
            harga = s.get('HARGA', 0)
            ma20 = s.get('MA20', 0)
            ma50 = s.get('MA50', 0)
            pbv = s.get('PBV', 0)
            
            ticker_clean = s.get('TICKER', 'XX').replace('.JK', '').lower()
            url_logo = f"https://logo.clearbit.com/{ticker_clean}.co.id?size=100"
            
            html_header = f"""
            <div class="pro-card">
                <div class="header-profile">
                    <div style="display:flex; align-items:center;">
                        <div style="width: 45px; height: 45px; border-radius: 10px; background: white; display: flex; justify-content: center; align-items: center; margin-right: 12px; overflow: hidden; border: 1px solid #27272A; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                            <img src="{url_logo}" onerror="this.src='https://via.placeholder.com/45/C6A87C/050505?text={s.get('TICKER', 'XX')[:2]}'" style="width: 100%; height: 100%; object-fit: contain;">
                        </div>
                        <div>
                            <div class="ticker-title">{s.get('TICKER', '')} <span class="badge-primary">V17.9.8</span></div>
                            <div class="ticker-desc">{s.get('NAME', '')}</div>
                            <div style="color:#C6A87C; font-size:10px; font-weight:600; margin-top:2px;">{s.get('SECTOR', 'Sektor Tidak Dikenal')} • {s.get('INDUSTRY', 'Industri Tidak Dikenal')}</div>
                        </div>
                    </div>
                    <div class="score-box">
                        <div style="font-size:9px; color:#71717A; letter-spacing:1px; text-transform:uppercase; font-weight:700;">Skor WPI</div>
                        <div class="score-value">{s.get('WPI_SCORE', 0):.1f}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_header, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1.5, 1])
            with col1:
                html_col1 = f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">⚡ STRATEGI RINGKASAN & HASIL%</div>
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #27272A; padding-bottom: 8px;">
                        <div><span class="data-label">FUNDAMENTAL</span><span class="data-value" style="font-size:12px;">ROE <span style="color:#C6A87C;">{s.get('ROE', 0)}%</span> | PBV <span style="color:#C6A87C;">{pbv}x</span> | YIELD <span style="color:#C6A87C;">{s.get('YIELD', '0%')}</span></span></div>
                        <div style="text-align:right;"><span class="data-label">ALIRAN BANDAR</span><span class="data-value" style="font-size:15px; color: {'#10B981' if 'AKUMULASI' in status_bandar else '#C6A87C' if 'NETRAL' in status_bandar else '#EF4444'};">{status_bandar}</span></div>
                    </div>
                    <div class="meter-container"><div class="meter-fill" style="width: {s.get('WPI_SCORE', 0)}%;"></div></div>
                    <div class="meter-labels"><span>BEARISH</span><span>NETRAL</span><span>BULLISH</span></div>
                </div>
                """
                st.markdown(html_col1, unsafe_allow_html=True)
                
            with col2:
                html_col2 = f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">🌊 UANG CERDAS</div>
                    <div style="text-align:center; margin: 4px 0;">
                        <div style="font-size:30px; font-weight:800; color:{'#10B981' if vol > vol_sma else '#A1A1AA'};">{vol/1000000:.1f}M</div>
                        <div class="badge-{'green' if vol > vol_sma else 'red'}" style="display:inline-block; margin-top:4px; font-size:11px; padding:3px 8px;">{'VOLUME SPIKE' if vol > vol_sma else 'VOLUME DRY'}</div>
                    </div>
                    <div style="text-align:center; font-size:11px; font-weight:700; margin-top:8px; border-top: 1px solid #27272A; padding-top:6px; color:#EF4444;">SIG: {serok_sig}</div>
                </div>
                """
                st.markdown(html_col2, unsafe_allow_html=True)
                
            # Bagian "Kondisi Harga & Bid/Offer" - Kotak "Entry & Stop Loss" dihilangkan sesuai permintaan
            cond_price = "badge-green" if harga > ma20 else "badge-red"
            cond_ma = "badge-green" if ma20 > ma50 else "badge-red"
            cond_macd = "badge-green" if s.get('MACD_BULLISH') else "badge-red"
            
            bid_val = int(s.get('BID', 0))
            ask_val = int(s.get('ASK', 0))
            bid_size = int(s.get('UKURAN_PENAWARAN', 0))
            ask_size = int(s.get('UKURAN_TANYA', 0))
            
            html_col3 = f"""
            <div class="pro-card">
                <div class="card-label">📈 KONDISI HARGA & BID/OFFER</div>
                <div class="data-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div><span class="data-label">HARGA TERAKHIR</span><span class="data-value">{int(harga):,}</span></div>
                    <div><span class="data-label">VOLATILITAS</span><span class="data-value" style="color: {'#EF4444' if volatility_badge == 'TINGGI' else '#10B981'};">{volatility_badge}</span></div>
                    <div><span class="data-label">MA20 (EMA)</span><span class="data-value">{int(ma20):,}</span></div>
                    <div><span class="data-label">EPS</span><span class="data-value">{float(s.get('EPS', 0)):,.2f}</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; text-align:center; margin-top:12px; border-top:1px dashed #27272A; border-bottom:1px dashed #27272A; padding:8px 0; background: rgba(5,5,5,0.5); border-radius: 6px;">
                    <div style="flex:1; border-right:1px solid #27272A;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">BID VOL</div>
                        <div style="font-size:11px; color:#10B981;">{bid_size:,}</div>
                    </div>
                    <div style="flex:1; border-right:1px solid #27272A;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">BID</div>
                        <div style="font-size:13px; color:#10B981; font-weight:800;">{bid_val:,}</div>
                    </div>
                    <div style="flex:1; border-right:1px solid #27272A;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">OFFER</div>
                        <div style="font-size:13px; color:#EF4444; font-weight:800;">{ask_val:,}</div>
                    </div>
                    <div style="flex:1;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">OFFR VOL</div>
                        <div style="font-size:11px; color:#EF4444;">{ask_size:,}</div>
                    </div>
                </div>
                <div style="margin-top:10px; display:flex; gap:4px; flex-wrap:wrap;">
                    <span class="{cond_price}">• P>MA20</span>
                    <span class="{cond_ma}">• MA20>MA50</span>
                    <span class="{cond_macd}">• MACD GOLDEN</span>
                </div>
            </div>
            """
            st.markdown(html_col3, unsafe_allow_html=True)
                
            if "BELI" in action_text or "AKUMULASI" in action_text:
                ai_insight = f"Sinyal Beli Kuat! Terdeteksi {status_bandar} di area krusial. Momentum didukung oleh sinyal {serok_sig}. Eksekusi di area ini memberikan potensi pantulan (Jackpot) dengan risiko Cut Loss yang sangat terukur."
            elif "SPEKULATIF" in action_text:
                ai_insight = f"Sinyal Spekulatif. Terdeteksi {status_bandar} di area pantul. Indikator teknikal menunjukkan {serok_sig}. Masuk dengan lot bertahap (Speculative Buy) dan siapkan strategi averaging jika koreksi wajar terjadi."
            else:
                ai_insight = f"Wait & See. Tekanan penjualan masih mendominasi atau harga tertahan di area nanggung ({status_bandar}). Pantau pergerakan harga hingga kembali masuk ke area Support / Entry Area sebelum mengambil keputusan."
                
            master_strategy_box = f"""
            <div class="pro-card" style="border: 2px solid {action_color}; background: linear-gradient(145deg, #18181B, #09090B);">
                <div class="card-label" style="color: {action_color}; justify-content: space-between;">
                    <span>🛡️ FINAL STRATEGI PUSAT KEPUTUSAN</span>
                    <span>{grade}</span>
                </div>
                <div style="background: {action_bg}; border: 1px solid {action_color}; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;">
                    <div style="color: {action_color}; font-size: 18px; font-weight: 800; letter-spacing: 0.5px;">{action_text}</div>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; background: rgba(5,5,5,0.6); border: 1px solid #27272A; border-radius: 8px; padding: 10px; margin-bottom: 12px; text-align:center;">
                    <div>
                        <div style="font-size:9px; color:#71717A; text-transform:uppercase; font-weight:700;">🎯 Area Masuk</div>
                        <div style="font-size:16px; font-weight:800; color:#FAFAFA; margin-top:2px;">{int(s.get('AREA BELI', 0)):,}</div>
                    </div>
                    <div style="width:1px; background:#27272A; height:30px;"></div>
                    <div>
                        <div style="font-size:9px; color:#71717A; text-transform:uppercase; font-weight:700;">🚨 Stop Loss</div>
                        <div style="font-size:16px; font-weight:800; color:#EF4444; margin-top:2px;">{int(s.get('TRAILING STOP', 0)):,}</div>
                    </div>
                </div>
                <div style="background-color: rgba(198, 168, 124, 0.05); border-left: 4px solid #C6A87C; padding: 12px; border-radius: 6px; border: 1px solid #27272A;">
                    <div style="color: #C6A87C; font-weight: 800; font-size: 10px; margin-bottom: 4px; display: flex; align-items: center; letter-spacing: 1px;">
                        <span style="font-size: 12px; margin-right: 6px;">🤖</span> KESIMPULAN EKSEKUTIF AI
                    </div>
                    <div style="font-size: 11px; color: #D4D4D8; line-height: 1.5;">{ai_insight}</div>
                </div>
            </div>
            """
            st.markdown(master_strategy_box, unsafe_allow_html=True)
            
            st.markdown("<h4 style='color:#C6A87C; font-size:12px; font-weight:700; margin-top:20px; margin-bottom:5px; text-transform:uppercase; letter-spacing:1px;'>📊 Kinerja Keuangan (Triwulanan)</h4>", unsafe_allow_html=True)
            
            with st.spinner(f"Data Pendapatan Bersih & Arus Kas {s.get('TICKER')}..."):
                df_q = fetch_quarterly_financials(s.get('TICKER') + ".JK")
                if df_q is not None and not df_q.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_q['Quarter'],
                        y=df_q['Laba Bersih'],
                        name='Pendapatan Bersih',
                        marker_color='#3B82F6',
                        text=[format_rupiah_short(v) for v in df_q['Laba Bersih']],
                        textposition='auto',
                        textfont=dict(color='white', size=10)
                    ))
                    fig.add_trace(go.Bar(
                        x=df_q['Quarter'],
                        y=df_q['Arus Kas Operasional'],
                        name='Operasi CF',
                        marker_color='#10B981',
                        text=[format_rupiah_short(v) for v in df_q['Arus Kas Operasional']],
                        textposition='auto',
                        textfont=dict(color='white', size=10)
                    ))
                    
                    fig.update_layout(
                        barmode='group',
                        dragmode=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#A1A1AA', size=11),
                        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'),
                        margin=dict(l=0, r=0, t=30, b=0),
                        yaxis=dict(gridcolor='#27272A', zerolinecolor='#27272A', showticklabels=False, fixedrange=True),
                        xaxis=dict(gridcolor='rgba(0,0,0,0)', fixedrange=True),
                        height=280
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.markdown("<div style='background:rgba(239, 68, 68, 0.1); border:1px solid #EF4444; border-radius:6px; padding:10px; font-size:11px; color:#EF4444; text-align:center;'>Data Kuartalan tidak tersedia di database untuk emiten ini.</div>", unsafe_allow_html=True)
                    
            col7, col8 = st.columns([1.5, 1])
            with col7:
                html_col7 = f"""
                <div class="pro-card" style="height:100%; margin-top:10px;">
                    <div class="card-label">📏 RETRASEMENT FIBONACCI (120D)</div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px; padding-bottom:4px; border-bottom:1px dashed #27272A;">
                        <span style="color:#71717A;">100% (Tinggi)</span><span style="color:#FAFAFA;">{int(s.get('FIBO_MAX',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span style="color:#A1A1AA;">61.8% (Golden Pocket)</span><span style="color:#C6A87C; font-weight:700;">{int(s.get('FIBO_618',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span style="color:#A1A1AA;">50.0% (Keseimbangan)</span><span style="color:#FAFAFA; font-weight:600;">{int(s.get('FIBO_500',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span style="color:#A1A1AA;">38.2%</span><span style="color:#FAFAFA; font-weight:600;">{int(s.get('FIBO_382',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-top:4px; padding-top:4px; border-top:1px dashed #27272A;">
                        <span style="color:#71717A;">0% (Rendah)</span><span style="color:#FAFAFA;">{int(s.get('FIBO_MIN',0)):,}</span>
                    </div>
                </div>
                """
                st.markdown(html_col7, unsafe_allow_html=True)
                
            with col8:
                vwap_val = s.get('VWAP', 0)
                vwap_diff_pct = ((harga - vwap_val) / vwap_val) * 100 if vwap_val > 0 else 0
                vwap_badge = "badge-green" if harga > vwap_val else "badge-red"
                vwap_text = "BULLISH (P > VWAP)" if harga > vwap_val else "BEARISH (P < VWAP)"
                
                html_col8 = f"""
                <div class="pro-card" style="height:100%; margin-top:10px; text-align:center; display:flex; flex-direction:column; justify-content:center;">
                    <div class="card-label" style="justify-content:center; border:none; margin-bottom:0;">⚖️ VWAP (20D)</div>
                    <div style="font-size:22px; font-weight:800; color:{'#10B981' if harga > vwap_val else '#EF4444'}; margin-top:4px;">{int(vwap_val):,}</div>
                    <div style="color:#71717A; font-size:10px; margin-top:4px;">Selisih ke VWAP: <b style="color:{'#10B981' if vwap_diff_pct > 0 else '#EF4444'};">{vwap_diff_pct:+.2f}%</b></div>
                    <div style="margin-top:8px;"><span class="{vwap_badge}" style="font-size:9px; padding:3px 6px;">{vwap_text}</span></div>
                </div>
                """
                st.markdown(html_col8, unsafe_allow_html=True)
                
            t_low = s.get('TARGET_LOW', 0)
            t_mean = s.get('TARGET_MEAN', 0)
            t_high = s.get('TARGET_HIGH', 0)
            
            if t_mean > 0:
                rec_key = s.get('REC_KEY', 'Tidak Tersedia')
                rec_color = "badge-green" if "BUY" in rec_key else ("badge-red" if "SELL" in rec_key else "badge-primary")
                num_analysts = s.get('JUMLAH_ANALIS', 0)
                upside = round(((t_mean - harga) / harga) * 100, 1)
                
                min_val = min(t_low, harga, t_mean) if t_low > 0 else (harga * 0.8)
                max_val = max(t_high, harga, t_mean) if t_high > 0 else (harga * 1.2)
                range_val = max_val - min_val if max_val > min_val else 1
                
                cur_pct = max(0, min(100, ((harga - min_val) / range_val) * 100))
                avg_pct = max(0, min(100, ((t_mean - min_val) / range_val) * 100))
                
                html_analyst = f"""
                <div class="pro-card" style="margin-top: 5px;">
                    <div class="card-label">📊 WAWASAN ANALIS (KONSENSUS)</div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:15px; padding:0 5px;">
                        <div>
                            <span style="font-size:10px; color:#71717A; font-weight:600;">REKOMENDASI</span><br>
                            <span class="{rec_color}" style="font-size:11px; margin-top:4px; display:inline-block;">{rec_key} ({num_analysts})</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:10px; color:#71717A; font-weight:600;">POTENSI POSITIF</span><br>
                            <span style="font-size:17px; color:{'#10B981' if upside > 0 else '#EF4444'}; font-weight:800;">{'+' if upside > 0 else ''}{upside}%</span>
                        </div>
                    </div>
                    <div style="font-size:11px; color:#FAFAFA; font-weight:700; margin-bottom:12px; padding-left:5px;">Target Harga Analis</div>
                    <div style="position:relative; height:45px; margin: 0 15px;">
                        <div style="position:absolute; top:10px; left:0; right:0; height:3px; background:#27272A; border-radius:2px;"></div>
                        <div style="position:absolute; top:6px; left:0%; background:#71717A; width:10px; height:10px; border-radius:50%; border:2px solid #050505; transform:translateX(-50%);"></div>
                        <div style="position:absolute; top:20px; left:0%; font-size:10px; font-weight:600; color:#71717A; transform:translateX(-50%);">{int(t_low):,}</div>
                        <div style="position:absolute; top:6px; right:100%; background:#71717A; width:10px; height:10px; border-radius:50%; border:2px solid #050505; transform:translateX(50%);"></div>
                        <div style="position:absolute; top:20px; right:100%; font-size:10px; font-weight:600; color:#71717A; transform:translateX(50%);">{int(t_high):,}</div>
                        <div style="position:absolute; top:4px; left:{cur_pct}%; background:#FAFAFA; width:14px; height:14px; border-radius:50%; border:2px solid #050505; transform:translateX(-50%); z-index:2;"></div>
                        <div style="position:absolute; top:24px; left:{cur_pct}%; font-size:11px; color:#FAFAFA; font-weight:800; transform:translateX(-50%); background:#27272A; border:1px solid #71717A; padding:2px 6px; border-radius:4px; z-index:2;">{int(harga):,}<br><span style="font-size:8px; font-weight:400;">Saat Ini</span></div>
                        <div style="position:absolute; top:5px; left:{avg_pct}%; background:#3B82F6; width:12px; height:12px; border-radius:50%; border:2px solid #050505; transform:translateX(-50%); z-index:1;"></div>
                        <div style="position:absolute; top:-18px; left:{avg_pct}%; font-size:11px; color:#3B82F6; font-weight:800; transform:translateX(-50%); background:#09090B; border:1px solid #3B82F6; padding:2px 6px; border-radius:4px; white-space:nowrap; z-index:1;">{int(t_mean):,}<br><span style="font-size:8px; font-weight:400;">Rata-rata</span></div>
                    </div>
                </div>
                """
                st.markdown(html_analyst, unsafe_allow_html=True)
                
            dist_ma20 = ((harga - ma20) / ma20) * 100 if ma20 > 0 else 0
            dist_vwap = ((harga - vwap_val) / vwap_val) * 100 if vwap_val > 0 else 0
            
            insight_html = f"""
            <div class="pro-card" style="margin-top: 15px; border-left: 3px solid #3B82F6;">
                <div class="card-label" style="border:none; margin-bottom:8px; color:#3B82F6;">🧠 WAWASAN ANALISIS HARGA</div>
                <ul style="font-size:11px; color:#D4D4D8; padding-left:15px; margin-bottom:0; line-height:1.6;">
                    <li style="margin-bottom:6px;">Harga saat ini <b>{int(harga):,}</b> berada <b style="color:{'#10B981' if dist_ma20 > 0 else '#EF4444'};">{abs(dist_ma20):.1f}% {'di atas' if dist_ma20 > 0 else 'di bawah'}</b> garis ekuilibrium jangka pendek (MA20: {int(ma20):,}).</li>
                    <li style="margin-bottom:6px;">Secara intraday, harga <b style="color:{'#10B981' if dist_vwap > 0 else '#EF4444'};">{abs(dist_vwap):.1f}% {'lebih tinggi' if dist_vwap > 0 else 'lebih rendah'}</b> dari rata-rata volume tertimbang bandar (VWAP: {int(vwap_val):,}). {'Dorongan beli sedang solid.' if dist_vwap > 0 else 'Waspada potensi tekanan jual lebih lanjut.'}</li>
                    <li>Batas pengamanan / <i>Stop Loss</i> krusial disarankan pada area <b>{int(s.get('TRAILING STOP', 0)):,}</b>. Disiplin *Cut Loss* jika harga *breakdown* dan ditutup (closing) di bawah level ini.</li>
                </ul>
            </div>
            """
            st.markdown(insight_html, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: PENGELOMPOKAN OTOMATIS
    # ------------------------------------------
    with tab_cluster:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>🎯 Kategori Pilihan Engine</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        
        if not df_all.empty:
            st.markdown("<div class='sop-title'>🟢 Sinyal Serok Bawah (Rebound)</div>", unsafe_allow_html=True)
            if 'SEROK_SIGNAL' in df_all.columns:
                df_serok = df_all[~df_all['SEROK_SIGNAL'].str.contains("TDK ADA", na=False)]
                if not df_serok.empty:
                    cols_serok = ['TICKER', 'HARGA', 'SEROK_SIGNAL', 'STATUS_BANDAR']
                    safe_cols_serok = [c for c in cols_serok if c in df_serok.columns]
                    st.dataframe(df_serok[safe_cols_serok], hide_index=True, use_container_width=True)
                else:
                    st.markdown("<div style='color:#71717A; font-size:12px; margin-bottom:15px;'>Belum ada saham yang masuk kriteria Serok Bawah saat ini.</div>", unsafe_allow_html=True)
                    
            st.markdown("<div class='sop-title' style='margin-top:20px;'>💰 Investasi Dividen (Yield >= 2%)</div>", unsafe_allow_html=True)
            if 'YIELD_RAW' in df_all.columns:
                df_div = df_all[df_all['YIELD_RAW'] >= 2.0].sort_values(by='YIELD_RAW', ascending=False)
                if not df_div.empty:
                    cols_div = ['TICKER', 'HARGA', 'YIELD', 'ROE', 'PBV', 'PER']
                    safe_cols_div = [c for c in cols_div if c in df_div.columns]
                    st.dataframe(df_div[safe_cols_div], hide_index=True, use_container_width=True)
                    
            st.markdown("<div class='sop-title' style='margin-top:20px;'>🐳 Aliran Uang Cerdas (Akumulasi)</div>", unsafe_allow_html=True)
            if 'STATUS_BANDAR' in df_all.columns:
                df_bandar = df_all[df_all['STATUS_BANDAR'].str.contains("AKUMULASI", na=False) | df_all['STATUS_BANDAR'].str.contains("MARK-UP", na=False)]
                if not df_bandar.empty:
                    cols_bandar = ['TICKER', 'HARGA', 'STATUS_BANDAR', 'WPI_SCORE']
                    safe_cols_bandar = [c for c in cols_bandar if c in df_bandar.columns]
                    st.dataframe(df_bandar[safe_cols_bandar], hide_index=True, use_container_width=True)
        else:
            st.info("Data kosong. Silakan lakukan SCAN terlebih dahulu.")

    # ------------------------------------------
    # TAB 3: EKSPOR & DAFTAR PANTAU
    # ------------------------------------------
    with tab_export:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>📥 Ekspor Data ke HP (Excel/CSV)</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        if not df_all.empty:
            cols_to_export = ['TICKER', 'NAME', 'HARGA', 'VWAP', 'AREA BELI', 'TRAILING STOP', 'FIBO_618', 'FIBO_500', 'SETUP_GRADE', 'SEROK_SIGNAL', 'STATUS_BANDAR', 'WPI_SCORE', 'ROE', 'PBV', 'YIELD', 'EPS']
            safe_export_cols = [c for c in cols_to_export if c in df_all.columns]
            df_export = df_all[safe_export_cols]
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 UNDUH DAFTAR PANTAUAN (CSV)",
                data=csv_data,
                file_name=f"JG_Ultimate_Watchlist_{get_waktu_wib().replace(':', '')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Lakukan SCAN terlebih dahulu di sidebar sebelum melakukan ekspor.")

    # ------------------------------------------
    # TAB 4 : SOP & PANDUAN PENGGUNAAN
    # ------------------------------------------
    with tab_sop:
        st.markdown("""
<div class="sop-box">
<div class="sop-title">Cara Penggunaan (SOP)</div>
<ol style="margin-left: -15px;">
<li>Buka sidebar (garis tiga di pojok kiri atas).</li>
<li>Pilih Timeframe yang diinginkan (Daily untuk Swing, Weekly untuk Investing).</li>
<li>Tekan tombol <b>🔄 SCAN</b> untuk mengumpulkan data terbaru dari market.</li>
<li>Buka Tab <b>DASHBOARD</b> untuk memantau 1 saham secara detail, atau buka Tab <b>CLUSTERING</b> untuk melihat saham pilihan algoritma secara massal.</li>
<li>Gunakan Tab <b>EXPORT</b> untuk menyimpan hasil scan ke HP Anda.</li>
</ol>
</div>

<div class="sop-box">
<div class="sop-title">Penjabaran Hasil Data Reel</div>
<ul style="margin-left: -15px; margin-bottom:0;">
<li style="margin-bottom:8px;"><b>Teknikal & MACD:</b> Menggunakan MA20 & MA50, diperkuat oleh MACD Golden Cross. Jika <i>Price > MA20</i> dan MACD Bullish, konfirmasi trend naik sangat kuat.</li>
<li style="margin-bottom:8px;"><b>WPI (Whale Pressure Index):</b> Indikator skor dari 0-100 yang mengukur seberapa kuat tekanan pembeli. Skor > 70 menunjukkan dominasi <i>buyer/bandar</i> yang kuat.</li>
<li style="margin-bottom:8px;"><b>Bandarmologi:</b> Menganalisa anomali Volume yang melonjak (Volume Spike) lalu dikawinkan dengan bentuk <i>Candlestick shadow</i>.</li>
<li style="margin-bottom:8px;"><b>Fundamental (ROE, PBV, EPS & YIELD):</b> <b>ROE</b> efisiensi laba (>10%), <b>PBV</b> valuasi saham (semakin rendah = murah), <b>EPS</b> adalah laba bersih per lembar saham, dan <b>YIELD</b> keuntungan dari Dividen rutin.</li>
<li style="margin-bottom:8px;"><b>Analyst Insights:</b> Data konsensus dari analis Wall Street yang menampilkan target proyeksi harga rata-rata institusi asing terhadap emiten tersebut.</li>
</ul>
</div>
""", unsafe_allow_html=True) 



streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import pytz
import warnings
import gc
import json
import os
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

# ==========================================
# 0. MESIN REAKTIF & CACHE PERSISTEN (V17.9.8)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v1798.json"

def load_reactive_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
            loaded_stocks = cache_data.get("raw_stocks", [])
            ihsg_data = cache_data.get("ihsg", {"val": 0, "change": 0})
            if loaded_stocks and isinstance(loaded_stocks, list):
                return loaded_stocks, cache_data.get("last_update", None), ihsg_data
        except:
            pass
    return [], None, {"val": 0, "change": 0}

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update, st.session_state.ihsg_data = load_reactive_cache()
if "reactive_mode" not in st.session_state:
    st.session_state.reactive_mode = False
if "current_tf" not in st.session_state:
    st.session_state.current_tf = "1 Hari (Harian)"

# ==========================================
# 1. UI MEWAH & CSS MOBILE EKSTREM
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v17.9.8", page_icon="✨", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: #050505 !important; color: #A1A1AA !important; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 3.5rem !important; padding-bottom: 1rem !important; max-width: 100% !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
section[data-testid="stSidebar"] { background-color: #09090B !important; border-right: 1px solid #1F1F22 !important; min-width: 180px !important; max-width: 180px !important; }
section[data-testid="stSidebar"] * { color: #A1A1AA !important; }
div[data-baseweb="select"] > div { background-color: #09090B !important; border: 1px solid #27272A !important; border-radius: 8px !important; padding: 4px !important; }
div[data-baseweb="select"] span { color: #FAFAFA !important; font-weight: 600 !important; font-size: 14px !important; }
.pro-card { background: linear-gradient(145deg, #121214, #09090B); border: 1px solid #27272A; border-radius: 10px; padding: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 10px; }
.market-banner { background: linear-gradient(145deg, #18181B, #09090B); border: 1px solid #3F3F46; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
.card-label { color: #C6A87C; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 6px;}
.header-profile { display: flex; justify-content: space-between; align-items: center; }
.ticker-title { font-size: 24px; font-weight: 800; color: #FAFAFA; line-height: 1.1; display: flex; align-items: center; gap: 6px;}
.ticker-desc { color: #A1A1AA; font-size: 12px; font-weight: 500; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px;}
.badge-primary { background: rgba(198, 168, 124, 0.1); color: #C6A87C; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(198, 168, 124, 0.3);}
.badge-green { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
.badge-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
.badge-blue { background: rgba(59, 130, 246, 0.1); color: #3B82F6; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.3);}
.score-box { background: #050505; border: 1px solid #27272A; border-radius: 8px; padding: 10px 14px; text-align: center; }
.score-value { font-size: 32px; font-weight: 800; color: #C6A87C; line-height: 1; margin: 4px 0;}
.data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;}
.data-label { font-size: 10px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; display: block;}
.data-value { font-size: 14px; color: #FAFAFA; font-weight: 700; display: block;}
.meter-container { background: #27272A; height: 6px; border-radius: 3px; margin-top: 15px; position: relative;}
.meter-fill { background: linear-gradient(90deg, #EF4444 0%, #C6A87C 50%, #10B981 100%); height: 100%; border-radius: 3px;}
.meter-labels { display: flex; justify-content: space-between; font-size: 10px; color: #71717A; font-weight: 600; margin-top: 4px;}
.stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 0px;}
.stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 600; background: transparent; padding: 8px 6px; border: none; font-size: 12px;}
.stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
.sop-box { background: #09090B; border-left: 3px solid #C6A87C; padding: 12px; margin-bottom: 15px; font-size: 12px; color: #D4D4D8; line-height:1.6;}
.sop-title { color: #C6A87C; font-weight: 700; font-size: 14px; margin-bottom: 8px; text-transform: uppercase;}
div[data-baseweb="input"] { background-color: #050505 !important; border: 1px solid #27272A !important; border-radius: 6px !important; }
div[data-baseweb="input"] input { color: #FAFAFA !important; font-size: 13px !important; }
@media (max-width: 768px) {
    .ticker-title { font-size: 18px; }
    .ticker-desc { font-size: 11px; max-width: 140px; white-space: normal; line-height: 1.2; }
    .score-box { padding: 6px 10px; }
    .score-value { font-size: 24px; }
    .data-grid { grid-template-columns: 1fr 1fr !important; }
    .market-banner { flex-direction: column; text-align: center; gap: 6px; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PENGAMBILAN DATA MESIN INTI & INDIKATOR
# ==========================================
MASTER_UNIVERSE = [
    "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT",
    "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM",
    "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR",
    "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR",
    "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS",
    "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP",
    "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE",
    "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH",
    "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA",
    "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS",
    "BBYB", "AGRO", "ARKA", "TOTO", "MLBI", "INDY", "PTRO", "MBAP", "BSSR", "SMMT",
    "KKGI", "ABMM", "CFIN", "MFIN", "ADMF", "BBKP", "PNBN", "BNLI", "SAGE", "GZCO",
    "STRK", "WIFI", "AEGS", "GOLF", "FILM", "ELSA", "RAJA", "HATM", "KRYA", "BSBK",
    "DATA", "NICL", "PAMG", "TRJA", "CARS", "BAPA", "KIJA", "DILD", "LPCK"
]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib():
    return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M")

def fetch_ihsg():
    try:
        tkr = yf.Ticker("^JKSE")
        hist = tkr.history(period="5d")
        if len(hist) >= 2:
            sekarang = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            perubahan = ((sekarang - prev) / prev) * 100
            return {"val": sekarang, "change": perubahan}
    except:
        pass
    return {"val": 0, "change": 0}

def get_dynamic_market_roster():
    try:
        df_batch = yf.download(master_tickers, period="5d", group_by="ticker", threads=True, progress=False)
        market_data = []
        for ticker in master_tickers:
            try:
                if isinstance(df_batch.columns, pd.MultiIndex):
                    df_t = df_batch[ticker].dropna()
                else:
                    df_t = df_batch.dropna()
                if len(df_t) < 2:
                    continue
                
                close_now = float(df_t['Close'].iloc[-1])
                close_prev = float(df_t['Close'].iloc[-2])
                vol_now = float(df_t['Volume'].iloc[-1])
                
                if close_now < 50 or vol_now < 50000:
                    continue
                    
                pct_change = ((close_now - close_prev) / close_prev) * 100
                trans_val = close_now * vol_now
                market_data.append({'Ticker': ticker, 'Change': pct_change, 'TransVal': trans_val, 'VolatilityScore': abs(pct_change) * trans_val})
            except:
                continue
                
        df_market = pd.DataFrame(market_data)
        if df_market.empty:
            return master_tickers[:300]
            
        top_gainers = df_market.nlargest(100, 'Change')['Ticker'].tolist()
        top_liquid = df_market.nlargest(100, 'TransVal')['Ticker'].tolist()
        top_volatile = df_market.nlargest(100, 'VolatilityScore')['Ticker'].tolist()
        return list(set(top_gainers + top_liquid + top_volatile))[:300]
    except:
        return master_tickers[:300]

@st.cache_data(ttl=3600)
def fetch_quarterly_financials(ticker):
    try:
        tkr = yf.Ticker(ticker)
        inc_stmt = tkr.quarterly_income_stmt
        if inc_stmt is None or inc_stmt.empty:
            inc_stmt = tkr.quarterly_financials
            
        cf_stmt = tkr.quarterly_cash_flow
        if cf_stmt is None or cf_stmt.empty:
            cf_stmt = tkr.quarterly_cashflow
            
        net_income_series = None
        if inc_stmt is not None and not inc_stmt.empty:
            for idx in inc_stmt.index:
                if 'net income' in str(idx).lower() and 'continuous' not in str(idx).lower():
                    net_income_series = inc_stmt.loc[idx]
                    break
            if net_income_series is None and "Net Income" in inc_stmt.index:
                net_income_series = inc_stmt.loc["Net Income"]
                
        op_cf_series = None
        if cf_stmt is not None and not cf_stmt.empty:
            for idx in cf_stmt.index:
                if 'operating cash flow' in str(idx).lower() or 'total cash from operating activities' in str(idx).lower():
                    op_cf_series = cf_stmt.loc[idx]
                    break
            if op_cf_series is None and "Operating Cash Flow" in cf_stmt.index:
                op_cf_series = cf_stmt.loc["Operating Cash Flow"]
                
        if net_income_series is None and op_cf_series is None:
            return None
            
        tanggal = []
        if net_income_series is not None:
            tanggal.extend(list(net_income_series.index))
        if op_cf_series is not None:
            tanggal.extend(list(op_cf_series.index))
            
        tanggal = sorted(list(set(tanggal)))
        data = {'Tanggal': tanggal, 'Laba Bersih': [], 'Arus Kas Operasional': []}
        
        for d in tanggal:
            ni_val = net_income_series.get(d, 0) if net_income_series is not None else 0
            cf_val = op_cf_series.get(d, 0) if op_cf_series is not None else 0
            data['Laba Bersih'].append(ni_val if not pd.isna(ni_val) else 0)
            data['Arus Kas Operasional'].append(cf_val if not pd.isna(cf_val) else 0)
            
        df_chart = pd.DataFrame(data)
        df_chart['Tanggal'] = pd.to_datetime(df_chart['Tanggal'])
        df_chart = df_chart.sort_values('Tanggal', ascending=True)
        df_chart['Quarter'] = df_chart['Tanggal'].dt.to_period('Q').astype(str)
        return df_chart
    except:
        return None

def format_rupiah_short(val):
    if val == 0 or pd.isna(val):
        return "-"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e12:
        return f"{sign}{abs_val/1e12:.1f}T"
    elif abs_val >= 1e9:
        return f"{sign}{abs_val/1e9:.1f}B"
    elif abs_val >= 1e6:
        return f"{sign}{abs_val/1e6:.1f}M"
    else:
        return f"{sign}{abs_val:,.0f}"

def hitung_rsi(df, periods=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/periods, min_periods=periods).mean()
    loss = (-1 * delta.clip(upper=0)).ewm(alpha=1/periods, min_periods=periods).mean()
    return 100 - (100 / (1 + (gain / loss)))

def hitung_stochastic(df, k_period=14, d_period=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min + 1e-9))
    return stoch_k, stoch_k.rolling(window=d_period).mean()

def check_bullish_divergence(df, window=20):
    try:
        recent = df.tail(window)
        if len(recent) < window:
            return False
        p_min1_idx = recent['Low'].iloc[:-5].idxmin()
        p_min2_idx = recent['Low'].iloc[-5:].idxmin()
        if (recent.loc[p_min2_idx, 'Low'] < recent.loc[p_min1_idx, 'Low']) and (recent.loc[p_min2_idx, 'RSI'] > recent.loc[p_min1_idx, 'RSI']):
            return True
    except:
        pass
    return False

def hitung_atr(df, periode=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    return np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1).rolling(periode).mean()

def fetch_single_stock(emiten, mode_tf):
    try:
        per, inv = "1y", "1d"
        kode = emiten.replace(".JK", "")
        tkr = yf.Ticker(emiten)
        df = tkr.history(period=per, interval=inv)
        if df.empty:
            return None
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        df = df.ffill().dropna(subset=['Close'])
        
        if len(df) < 30:
            return None
            
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = hitung_rsi(df)
        df['Stoch_K'], df['Stoch_D'] = hitung_stochastic(df)
        df['ATR'] = hitung_atr(df)
        df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Chandelier_Exit'] = df['High'].rolling(22).max() - (df['ATR'] * 3.0)
        
        harga_tipikal = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (harga_tipikal * df['Volume']).rolling(window=20).sum() / df['Volume'].rolling(window=20).sum()
        vwap_skg = float(df['VWAP'].iloc[-1]) if not pd.isna(df['VWAP'].iloc[-1]) else float(df['Close'].iloc[-1])
        
        fibo_window = df.tail(120)
        max_h = float(fibo_window['High'].max())
        min_l = float(fibo_window['Low'].min())
        fibo_diff = max_h - min_l
        fibo_236 = max_h - 0.236 * fibo_diff
        fibo_382 = max_h - 0.382 * fibo_diff
        fibo_500 = max_h - 0.500 * fibo_diff
        fibo_618 = max_h - 0.618 * fibo_diff
        
        df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        macd_val = float(df['MACD'].iloc[-1])
        sig_val = float(df['Signal_Line'].iloc[-1])
        macd_bullish = macd_val > sig_val
        
        harga_skg = float(df['Close'].iloc[-1])
        open_skg = float(df['Open'].iloc[-1])
        high_skg = float(df['High'].iloc[-1])
        low_skg = float(df['Low'].iloc[-1])
        vol_skg = float(df['Volume'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        ema20_skg = float(df['EMA20'].iloc[-1])
        sma50_skg = float(df['SMA50'].iloc[-1])
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        low_20 = float(df['Low'].tail(20).min())
        
        is_near_bottom = (harga_skg - low_20) / low_20 <= 0.06
        has_bullish_div = check_bullish_divergence(df, window=20)
        is_bullish = harga_skg >= open_skg
        body_size = abs(open_skg - harga_skg)
        lower_shadow = (open_skg if is_bullish else harga_skg) - low_skg
        
        is_whale_absorption = (vol_skg > vol_sma20 * 1.3) and (lower_shadow > body_size * 1.5) and is_near_bottom
        
        if has_bullish_div and is_near_bottom:
            serok_signal = "🎯 DIVERGENSI BULLISH"
        elif is_whale_absorption:
            serok_signal = "🐳 PENYERAPAN PAUS"
        elif (float(df['Stoch_K'].iloc[-1]) < 30) and (float(df['Stoch_K'].iloc[-1]) > float(df['Stoch_D'].iloc[-1])) and is_near_bottom:
            serok_signal = "🟢 OVERSOLD REBOUND"
        else:
            serok_signal = "➖ TDK ADA"
            
        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg:
            trailing_stop = harga_skg - (float(df['ATR'].iloc[-1]) * 2)
            
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        is_vol_spike = vol_skg > (vol_sma20 * 1.2)
        
        if is_vol_spike:
            if lower_shadow > (body_size * 1.5):
                status_bandar = "🐳 AKUMULASI BAWAH"
            elif upper_shadow > (body_size * 1.5):
                status_bandar = "🩸 DISTRIBUSI PUCUK"
            elif is_bullish and wpi_score > 70:
                status_bandar = "🚀 MARK-UP BERINGAS"
            elif is_bullish:
                status_bandar = "🟢 AKUMULASI AWAL"
            else:
                status_bandar = "💥 MARK-DOWN"
        else:
            status_bandar = "➖ NETRAL"
            
        setup_score = sum([harga_skg > ema20_skg, wpi_score > 85, vol_skg > vol_sma20*2, "TDK ADA" not in serok_signal, macd_bullish])
        
        if "TDK ADA" not in serok_signal:
            setup_grade = "🎯 SETUP JACKPOT"
        elif setup_score >= 3 and wpi_score >= 70:
            setup_grade = "⭐ SETUP A+"
        elif setup_score >= 2 and wpi_score >= 80:
            setup_grade = "⚡ SETUP AGRESIF"
        elif setup_score >= 1:
            setup_grade = "✔️ SETUP B"
        else:
            setup_grade = "⚠️ WAIT/WATCHLIST"
            
        info = tkr.info if hasattr(tkr, 'info') and tkr.info else {}
        sector_val = info.get('sector', 'Sektor Tidak Tersedia')
        industry_val = info.get('industry', 'Industri Tidak Tersedia')
        
        div_rate = info.get('dividendRate', 0)
        raw_yield = info.get('dividendYield', 0)
        
        if div_rate and div_rate > 0 and harga_skg > 0:
            div_yield = (div_rate / harga_skg) * 100
        else:
            div_yield = (raw_yield * 100) if (raw_yield and raw_yield < 1) else (raw_yield if raw_yield else 0.0)
        div_yield = round(div_yield, 2)
        
        roe_raw = info.get('returnOnEquity', 0)
        roe_pct = round(roe_raw * 100, 2) if roe_raw else 0.0
        
        per_val = info.get('trailingPE', 0.0)
        pbv_val = info.get('priceToBook', 0)
        
        if pbv_val and pbv_val > 100:
            if per_val and roe_raw:
                pbv_val = per_val * roe_raw
            else:
                pbv_val = pbv_val / 16000
        pbv_val = round(pbv_val, 2) if pbv_val else 0.0
        eps_val = float(info.get('trailingEps', 0.0))
        
        target_low = info.get('targetLowPrice', 0)
        target_mean = info.get('targetMeanPrice', 0)
        target_high = info.get('targetHighPrice', 0)
        rec_key = str(info.get('recommendationKey', 'none')).replace('_', ' ').upper()
        num_analysts = info.get('numberOfAnalystOpinions', 0)
        
        bid_price = info.get('bid', 0)
        ask_price = info.get('ask', 0)
        bid_size = info.get('bidSize', 0)
        ask_size = info.get('askSize', 0)
        
        return {
            "TICKER": kode,
            "HARGA": harga_skg,
            "MA20": ema20_skg,
            "MA50": sma50_skg,
            "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3),
            "TRAILING STOP": trailing_stop,
            "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal,
            "STATUS_BANDAR": status_bandar,
            "SETUP_GRADE": setup_grade,
            "PER": round(per_val, 2) if per_val else 0.0,
            "ROE": roe_pct,
            "YIELD": f"{div_yield}%",
            "YIELD_RAW": div_yield,
            "PBV": pbv_val,
            "EPS": eps_val,
            "RET_1D": ((harga_skg - prev_close) / prev_close * 100),
            "VOLUME": vol_skg,
            "VOL_SMA20": vol_sma20,
            "ATR_PCT": (float(df['ATR'].iloc[-1]) / harga_skg) * 100,
            "NAME": info.get('longName', kode),
            "SECTOR": sector_val,
            "INDUSTRY": industry_val,
            "MACD_BULLISH": macd_bullish,
            "TARGET_LOW": target_low,
            "TARGET_MEAN": target_mean,
            "TARGET_HIGH": target_high,
            "REC_KEY": rec_key,
            "JUMLAH_ANALIS": num_analysts,
            "VWAP": vwap_skg,
            "FIBO_236": fibo_236,
            "FIBO_382": fibo_382,
            "FIBO_500": fibo_500,
            "FIBO_618": fibo_618,
            "FIBO_MAX": max_h,
            "FIBO_MIN": min_l,
            "BID": bid_price,
            "ASK": ask_price,
            "UKURAN_PENAWARAN": bid_size,
            "UKURAN_TANYA": ask_size
        }
    except Exception as e:
        return None

# ==========================================
# 3. SIDEBAR (KEMEWAHAN ULTRA-SEMPIT)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#C6A87C; font-size:16px; font-weight:800; margin-bottom:0;'>✨ JG ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#71717A; font-size:9px; letter-spacing:1px; margin-bottom:20px;'>EDISI V17.9.8</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:10px; color:#A1A1AA; margin-bottom:5px;'>⏱️ Jangka Waktu:</div>", unsafe_allow_html=True)
    tf_pilihan = st.selectbox("TF", ("1 Hari (Harian)", "1 Minggu (Mingguan)"), index=0, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='color:#FAFAFA; font-size:10px; font-weight:700; margin-bottom:5px;'>⚙️ AUTO-SYNC</div>", unsafe_allow_html=True)
    
    reactive_on = st.toggle("Mode Langsung", value=st.session_state.reactive_mode)
    if reactive_on != st.session_state.reactive_mode:
        st.session_state.reactive_mode = reactive_on
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 SCAN", use_container_width=True):
        st.session_state.raw_stocks = []
        
        radar_bar_ihsg = st.progress(0, text="Mengambil data IHSG...")
        st.session_state.ihsg_data = fetch_ihsg()
        radar_bar_ihsg.empty()
        
        radar_bar = st.progress(0, text="Mendeteksi Saham Aktif...")
        dynamic_tickers = get_dynamic_market_roster()
        radar_bar.empty()
        
        my_bar = st.progress(0, text=f"Memindai...")
        for i, t in enumerate(dynamic_tickers):
            my_bar.progress((i + 1) / len(dynamic_tickers), text=f"{t} ({i+1}/{len(dynamic_tickers)})")
            data = fetch_single_stock(t, tf_pilihan)
            if data:
                st.session_state.raw_stocks.append(data)
            gc.collect()
        my_bar.empty()
        
        st.session_state.last_update = get_waktu_wib()
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update, "ihsg": st.session_state.ihsg_data}, f)
        except:
            pass
        st.rerun()
        
    if st.session_state.last_update:
        st.markdown(f"<div style='font-size:8px; color:#71717A; text-align:center; margin-top:20px;'>Pembaruan Terakhir:<br>{st.session_state.last_update}</div>", unsafe_allow_html=True)

# ==========================================
# 4. TAB UTAMA
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN' di sidebar untuk memulai.")
else:
    tab_dash, tab_cluster, tab_export, tab_sop = st.tabs(["✨ DASHBOARD", "🎯 CLUSTER", "📥 EXPORT", "📖 SOP"])

    # ------------------------------------------
    # TAB 1: DASHBOARD MEWAH
    # ------------------------------------------
    with tab_dash:
        last_up_text = st.session_state.last_update if st.session_state.last_update else "Belum diset"
        ihsg = st.session_state.ihsg_data
        ihsg_val = ihsg.get("val", 0)
        ihsg_change = ihsg.get("change", 0)
        
        ihsg_color = "#10B981" if ihsg_change >= 0 else "#EF4444"
        ihsg_sign = "+" if ihsg_change >= 0 else ""
        
        market_banner_html = f"""
        <div class="market-banner">
            <div>
                <div style="font-size:10px; color:#A1A1AA; text-transform:uppercase; letter-spacing:1px; font-weight:700;">🇮🇩 IHSG (KOMPOSIT)</div>
                <div style="font-size:18px; font-weight:800; color:{ihsg_color}; margin-top:2px;">{ihsg_val:,.2f} <span style="font-size:12px; font-weight:600;">({ihsg_sign}{ihsg_change:.2f}%)</span></div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; color:#71717A;">Status Sinkronisasi</div>
                <div style="font-size:11px; font-weight:700; color:#C6A87C;">{last_up_text}</div>
            </div>
        </div>
        """
        st.markdown(market_banner_html, unsafe_allow_html=True)
        
        st.markdown("<div style='font-size:11px; color:#71717A; font-weight:700; margin-bottom:5px; text-transform:uppercase;'>🔍 Cari Emiten</div>", unsafe_allow_html=True)
        pilihan_ticker = st.selectbox("Pilih", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0, label_visibility="collapsed")
        
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            grade = s.get("SETUP_GRADE", "WAIT")
            atr_pct = s.get('ATR_PCT', 0)
            volatility_badge = "TINGGI" if atr_pct > 4 else "NORMAL"
            
            if "JACKPOT" in grade or "A+" in grade:
                action_text, action_color, action_bg = "BELI / AKUMULASIKAN", "#10B981", "rgba(16, 185, 129, 0.1)"
            elif "WAIT" in grade:
                action_text, action_color, action_bg = "TUNGGU / DAFTAR PANTAU", "#C6A87C", "rgba(198, 168, 124, 0.1)"
            else:
                action_text, action_color, action_bg = "BELI SPEKULATIF", "#FAFAFA", "rgba(250, 250, 250, 0.1)"
                
            vol = s.get('VOLUME', 0)
            vol_sma = s.get('VOL_SMA20', 1)
            status_bandar = s.get('STATUS_BANDAR', 'NETRAL')
            serok_sig = s.get('SEROK_SIGNAL', '➖ TDK ADA').split()[0]
            harga = s.get('HARGA', 0)
            ma20 = s.get('MA20', 0)
            ma50 = s.get('MA50', 0)
            pbv = s.get('PBV', 0)
            
            ticker_clean = s.get('TICKER', 'XX').replace('.JK', '').lower()
            url_logo = f"https://logo.clearbit.com/{ticker_clean}.co.id?size=100"
            
            html_header = f"""
            <div class="pro-card">
                <div class="header-profile">
                    <div style="display:flex; align-items:center;">
                        <div style="width: 45px; height: 45px; border-radius: 10px; background: white; display: flex; justify-content: center; align-items: center; margin-right: 12px; overflow: hidden; border: 1px solid #27272A; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                            <img src="{url_logo}" onerror="this.src='https://via.placeholder.com/45/C6A87C/050505?text={s.get('TICKER', 'XX')[:2]}'" style="width: 100%; height: 100%; object-fit: contain;">
                        </div>
                        <div>
                            <div class="ticker-title">{s.get('TICKER', '')} <span class="badge-primary">V17.9.8</span></div>
                            <div class="ticker-desc">{s.get('NAME', '')}</div>
                            <div style="color:#C6A87C; font-size:10px; font-weight:600; margin-top:2px;">{s.get('SECTOR', 'Sektor Tidak Dikenal')} • {s.get('INDUSTRY', 'Industri Tidak Dikenal')}</div>
                        </div>
                    </div>
                    <div class="score-box">
                        <div style="font-size:9px; color:#71717A; letter-spacing:1px; text-transform:uppercase; font-weight:700;">Skor WPI</div>
                        <div class="score-value">{s.get('WPI_SCORE', 0):.1f}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_header, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1.5, 1])
            with col1:
                html_col1 = f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">⚡ STRATEGI RINGKASAN & HASIL%</div>
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #27272A; padding-bottom: 8px;">
                        <div><span class="data-label">FUNDAMENTAL</span><span class="data-value" style="font-size:12px;">ROE <span style="color:#C6A87C;">{s.get('ROE', 0)}%</span> | PBV <span style="color:#C6A87C;">{pbv}x</span> | YIELD <span style="color:#C6A87C;">{s.get('YIELD', '0%')}</span></span></div>
                        <div style="text-align:right;"><span class="data-label">ALIRAN BANDAR</span><span class="data-value" style="font-size:15px; color: {'#10B981' if 'AKUMULASI' in status_bandar else '#C6A87C' if 'NETRAL' in status_bandar else '#EF4444'};">{status_bandar}</span></div>
                    </div>
                    <div class="meter-container"><div class="meter-fill" style="width: {s.get('WPI_SCORE', 0)}%;"></div></div>
                    <div class="meter-labels"><span>BEARISH</span><span>NETRAL</span><span>BULLISH</span></div>
                </div>
                """
                st.markdown(html_col1, unsafe_allow_html=True)
                
            with col2:
                html_col2 = f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">🌊 UANG CERDAS</div>
                    <div style="text-align:center; margin: 4px 0;">
                        <div style="font-size:30px; font-weight:800; color:{'#10B981' if vol > vol_sma else '#A1A1AA'};">{vol/1000000:.1f}M</div>
                        <div class="badge-{'green' if vol > vol_sma else 'red'}" style="display:inline-block; margin-top:4px; font-size:11px; padding:3px 8px;">{'VOLUME SPIKE' if vol > vol_sma else 'VOLUME DRY'}</div>
                    </div>
                    <div style="text-align:center; font-size:11px; font-weight:700; margin-top:8px; border-top: 1px solid #27272A; padding-top:6px; color:#EF4444;">SIG: {serok_sig}</div>
                </div>
                """
                st.markdown(html_col2, unsafe_allow_html=True)
                
            # Bagian "Kondisi Harga & Bid/Offer" - Kotak "Entry & Stop Loss" dihilangkan sesuai permintaan
            cond_price = "badge-green" if harga > ma20 else "badge-red"
            cond_ma = "badge-green" if ma20 > ma50 else "badge-red"
            cond_macd = "badge-green" if s.get('MACD_BULLISH') else "badge-red"
            
            bid_val = int(s.get('BID', 0))
            ask_val = int(s.get('ASK', 0))
            bid_size = int(s.get('UKURAN_PENAWARAN', 0))
            ask_size = int(s.get('UKURAN_TANYA', 0))
            
            html_col3 = f"""
            <div class="pro-card">
                <div class="card-label">📈 KONDISI HARGA & BID/OFFER</div>
                <div class="data-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div><span class="data-label">HARGA TERAKHIR</span><span class="data-value">{int(harga):,}</span></div>
                    <div><span class="data-label">VOLATILITAS</span><span class="data-value" style="color: {'#EF4444' if volatility_badge == 'TINGGI' else '#10B981'};">{volatility_badge}</span></div>
                    <div><span class="data-label">MA20 (EMA)</span><span class="data-value">{int(ma20):,}</span></div>
                    <div><span class="data-label">EPS</span><span class="data-value">{float(s.get('EPS', 0)):,.2f}</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; text-align:center; margin-top:12px; border-top:1px dashed #27272A; border-bottom:1px dashed #27272A; padding:8px 0; background: rgba(5,5,5,0.5); border-radius: 6px;">
                    <div style="flex:1; border-right:1px solid #27272A;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">BID VOL</div>
                        <div style="font-size:11px; color:#10B981;">{bid_size:,}</div>
                    </div>
                    <div style="flex:1; border-right:1px solid #27272A;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">BID</div>
                        <div style="font-size:13px; color:#10B981; font-weight:800;">{bid_val:,}</div>
                    </div>
                    <div style="flex:1; border-right:1px solid #27272A;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">OFFER</div>
                        <div style="font-size:13px; color:#EF4444; font-weight:800;">{ask_val:,}</div>
                    </div>
                    <div style="flex:1;">
                        <div style="font-size:8px; color:#71717A; font-weight:700;">OFFR VOL</div>
                        <div style="font-size:11px; color:#EF4444;">{ask_size:,}</div>
                    </div>
                </div>
                <div style="margin-top:10px; display:flex; gap:4px; flex-wrap:wrap;">
                    <span class="{cond_price}">• P>MA20</span>
                    <span class="{cond_ma}">• MA20>MA50</span>
                    <span class="{cond_macd}">• MACD GOLDEN</span>
                </div>
            </div>
            """
            st.markdown(html_col3, unsafe_allow_html=True)
                
            if "BELI" in action_text or "AKUMULASI" in action_text:
                ai_insight = f"Sinyal Beli Kuat! Terdeteksi {status_bandar} di area krusial. Momentum didukung oleh sinyal {serok_sig}. Eksekusi di area ini memberikan potensi pantulan (Jackpot) dengan risiko Cut Loss yang sangat terukur."
            elif "SPEKULATIF" in action_text:
                ai_insight = f"Sinyal Spekulatif. Terdeteksi {status_bandar} di area pantul. Indikator teknikal menunjukkan {serok_sig}. Masuk dengan lot bertahap (Speculative Buy) dan siapkan strategi averaging jika koreksi wajar terjadi."
            else:
                ai_insight = f"Wait & See. Tekanan penjualan masih mendominasi atau harga tertahan di area nanggung ({status_bandar}). Pantau pergerakan harga hingga kembali masuk ke area Support / Entry Area sebelum mengambil keputusan."
                
            master_strategy_box = f"""
            <div class="pro-card" style="border: 2px solid {action_color}; background: linear-gradient(145deg, #18181B, #09090B);">
                <div class="card-label" style="color: {action_color}; justify-content: space-between;">
                    <span>🛡️ FINAL STRATEGI PUSAT KEPUTUSAN</span>
                    <span>{grade}</span>
                </div>
                <div style="background: {action_bg}; border: 1px solid {action_color}; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;">
                    <div style="color: {action_color}; font-size: 18px; font-weight: 800; letter-spacing: 0.5px;">{action_text}</div>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; background: rgba(5,5,5,0.6); border: 1px solid #27272A; border-radius: 8px; padding: 10px; margin-bottom: 12px; text-align:center;">
                    <div>
                        <div style="font-size:9px; color:#71717A; text-transform:uppercase; font-weight:700;">🎯 Area Masuk</div>
                        <div style="font-size:16px; font-weight:800; color:#FAFAFA; margin-top:2px;">{int(s.get('AREA BELI', 0)):,}</div>
                    </div>
                    <div style="width:1px; background:#27272A; height:30px;"></div>
                    <div>
                        <div style="font-size:9px; color:#71717A; text-transform:uppercase; font-weight:700;">🚨 Stop Loss</div>
                        <div style="font-size:16px; font-weight:800; color:#EF4444; margin-top:2px;">{int(s.get('TRAILING STOP', 0)):,}</div>
                    </div>
                </div>
                <div style="background-color: rgba(198, 168, 124, 0.05); border-left: 4px solid #C6A87C; padding: 12px; border-radius: 6px; border: 1px solid #27272A;">
                    <div style="color: #C6A87C; font-weight: 800; font-size: 10px; margin-bottom: 4px; display: flex; align-items: center; letter-spacing: 1px;">
                        <span style="font-size: 12px; margin-right: 6px;">🤖</span> KESIMPULAN EKSEKUTIF AI
                    </div>
                    <div style="font-size: 11px; color: #D4D4D8; line-height: 1.5;">{ai_insight}</div>
                </div>
            </div>
            """
            st.markdown(master_strategy_box, unsafe_allow_html=True)
            
            st.markdown("<h4 style='color:#C6A87C; font-size:12px; font-weight:700; margin-top:20px; margin-bottom:5px; text-transform:uppercase; letter-spacing:1px;'>📊 Kinerja Keuangan (Triwulanan)</h4>", unsafe_allow_html=True)
            
            with st.spinner(f"Data Pendapatan Bersih & Arus Kas {s.get('TICKER')}..."):
                df_q = fetch_quarterly_financials(s.get('TICKER') + ".JK")
                if df_q is not None and not df_q.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_q['Quarter'],
                        y=df_q['Laba Bersih'],
                        name='Pendapatan Bersih',
                        marker_color='#3B82F6',
                        text=[format_rupiah_short(v) for v in df_q['Laba Bersih']],
                        textposition='auto',
                        textfont=dict(color='white', size=10)
                    ))
                    fig.add_trace(go.Bar(
                        x=df_q['Quarter'],
                        y=df_q['Arus Kas Operasional'],
                        name='Operasi CF',
                        marker_color='#10B981',
                        text=[format_rupiah_short(v) for v in df_q['Arus Kas Operasional']],
                        textposition='auto',
                        textfont=dict(color='white', size=10)
                    ))
                    
                    fig.update_layout(
                        barmode='group',
                        dragmode=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#A1A1AA', size=11),
                        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'),
                        margin=dict(l=0, r=0, t=30, b=0),
                        yaxis=dict(gridcolor='#27272A', zerolinecolor='#27272A', showticklabels=False, fixedrange=True),
                        xaxis=dict(gridcolor='rgba(0,0,0,0)', fixedrange=True),
                        height=280
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.markdown("<div style='background:rgba(239, 68, 68, 0.1); border:1px solid #EF4444; border-radius:6px; padding:10px; font-size:11px; color:#EF4444; text-align:center;'>Data Kuartalan tidak tersedia di database untuk emiten ini.</div>", unsafe_allow_html=True)
                    
            col7, col8 = st.columns([1.5, 1])
            with col7:
                html_col7 = f"""
                <div class="pro-card" style="height:100%; margin-top:10px;">
                    <div class="card-label">📏 RETRASEMENT FIBONACCI (120D)</div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px; padding-bottom:4px; border-bottom:1px dashed #27272A;">
                        <span style="color:#71717A;">100% (Tinggi)</span><span style="color:#FAFAFA;">{int(s.get('FIBO_MAX',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span style="color:#A1A1AA;">61.8% (Golden Pocket)</span><span style="color:#C6A87C; font-weight:700;">{int(s.get('FIBO_618',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span style="color:#A1A1AA;">50.0% (Keseimbangan)</span><span style="color:#FAFAFA; font-weight:600;">{int(s.get('FIBO_500',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span style="color:#A1A1AA;">38.2%</span><span style="color:#FAFAFA; font-weight:600;">{int(s.get('FIBO_382',0)):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-top:4px; padding-top:4px; border-top:1px dashed #27272A;">
                        <span style="color:#71717A;">0% (Rendah)</span><span style="color:#FAFAFA;">{int(s.get('FIBO_MIN',0)):,}</span>
                    </div>
                </div>
                """
                st.markdown(html_col7, unsafe_allow_html=True)
                
            with col8:
                vwap_val = s.get('VWAP', 0)
                vwap_diff_pct = ((harga - vwap_val) / vwap_val) * 100 if vwap_val > 0 else 0
                vwap_badge = "badge-green" if harga > vwap_val else "badge-red"
                vwap_text = "BULLISH (P > VWAP)" if harga > vwap_val else "BEARISH (P < VWAP)"
                
                html_col8 = f"""
                <div class="pro-card" style="height:100%; margin-top:10px; text-align:center; display:flex; flex-direction:column; justify-content:center;">
                    <div class="card-label" style="justify-content:center; border:none; margin-bottom:0;">⚖️ VWAP (20D)</div>
                    <div style="font-size:22px; font-weight:800; color:{'#10B981' if harga > vwap_val else '#EF4444'}; margin-top:4px;">{int(vwap_val):,}</div>
                    <div style="color:#71717A; font-size:10px; margin-top:4px;">Selisih ke VWAP: <b style="color:{'#10B981' if vwap_diff_pct > 0 else '#EF4444'};">{vwap_diff_pct:+.2f}%</b></div>
                    <div style="margin-top:8px;"><span class="{vwap_badge}" style="font-size:9px; padding:3px 6px;">{vwap_text}</span></div>
                </div>
                """
                st.markdown(html_col8, unsafe_allow_html=True)
                
            t_low = s.get('TARGET_LOW', 0)
            t_mean = s.get('TARGET_MEAN', 0)
            t_high = s.get('TARGET_HIGH', 0)
            
            if t_mean > 0:
                rec_key = s.get('REC_KEY', 'Tidak Tersedia')
                rec_color = "badge-green" if "BUY" in rec_key else ("badge-red" if "SELL" in rec_key else "badge-primary")
                num_analysts = s.get('JUMLAH_ANALIS', 0)
                upside = round(((t_mean - harga) / harga) * 100, 1)
                
                min_val = min(t_low, harga, t_mean) if t_low > 0 else (harga * 0.8)
                max_val = max(t_high, harga, t_mean) if t_high > 0 else (harga * 1.2)
                range_val = max_val - min_val if max_val > min_val else 1
                
                cur_pct = max(0, min(100, ((harga - min_val) / range_val) * 100))
                avg_pct = max(0, min(100, ((t_mean - min_val) / range_val) * 100))
                
                html_analyst = f"""
                <div class="pro-card" style="margin-top: 5px;">
                    <div class="card-label">📊 WAWASAN ANALIS (KONSENSUS)</div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:15px; padding:0 5px;">
                        <div>
                            <span style="font-size:10px; color:#71717A; font-weight:600;">REKOMENDASI</span><br>
                            <span class="{rec_color}" style="font-size:11px; margin-top:4px; display:inline-block;">{rec_key} ({num_analysts})</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:10px; color:#71717A; font-weight:600;">POTENSI POSITIF</span><br>
                            <span style="font-size:17px; color:{'#10B981' if upside > 0 else '#EF4444'}; font-weight:800;">{'+' if upside > 0 else ''}{upside}%</span>
                        </div>
                    </div>
                    <div style="font-size:11px; color:#FAFAFA; font-weight:700; margin-bottom:12px; padding-left:5px;">Target Harga Analis</div>
                    <div style="position:relative; height:45px; margin: 0 15px;">
                        <div style="position:absolute; top:10px; left:0; right:0; height:3px; background:#27272A; border-radius:2px;"></div>
                        <div style="position:absolute; top:6px; left:0%; background:#71717A; width:10px; height:10px; border-radius:50%; border:2px solid #050505; transform:translateX(-50%);"></div>
                        <div style="position:absolute; top:20px; left:0%; font-size:10px; font-weight:600; color:#71717A; transform:translateX(-50%);">{int(t_low):,}</div>
                        <div style="position:absolute; top:6px; right:100%; background:#71717A; width:10px; height:10px; border-radius:50%; border:2px solid #050505; transform:translateX(50%);"></div>
                        <div style="position:absolute; top:20px; right:100%; font-size:10px; font-weight:600; color:#71717A; transform:translateX(50%);">{int(t_high):,}</div>
                        <div style="position:absolute; top:4px; left:{cur_pct}%; background:#FAFAFA; width:14px; height:14px; border-radius:50%; border:2px solid #050505; transform:translateX(-50%); z-index:2;"></div>
                        <div style="position:absolute; top:24px; left:{cur_pct}%; font-size:11px; color:#FAFAFA; font-weight:800; transform:translateX(-50%); background:#27272A; border:1px solid #71717A; padding:2px 6px; border-radius:4px; z-index:2;">{int(harga):,}<br><span style="font-size:8px; font-weight:400;">Saat Ini</span></div>
                        <div style="position:absolute; top:5px; left:{avg_pct}%; background:#3B82F6; width:12px; height:12px; border-radius:50%; border:2px solid #050505; transform:translateX(-50%); z-index:1;"></div>
                        <div style="position:absolute; top:-18px; left:{avg_pct}%; font-size:11px; color:#3B82F6; font-weight:800; transform:translateX(-50%); background:#09090B; border:1px solid #3B82F6; padding:2px 6px; border-radius:4px; white-space:nowrap; z-index:1;">{int(t_mean):,}<br><span style="font-size:8px; font-weight:400;">Rata-rata</span></div>
                    </div>
                </div>
                """
                st.markdown(html_analyst, unsafe_allow_html=True)
                
            dist_ma20 = ((harga - ma20) / ma20) * 100 if ma20 > 0 else 0
            dist_vwap = ((harga - vwap_val) / vwap_val) * 100 if vwap_val > 0 else 0
            
            insight_html = f"""
            <div class="pro-card" style="margin-top: 15px; border-left: 3px solid #3B82F6;">
                <div class="card-label" style="border:none; margin-bottom:8px; color:#3B82F6;">🧠 WAWASAN ANALISIS HARGA</div>
                <ul style="font-size:11px; color:#D4D4D8; padding-left:15px; margin-bottom:0; line-height:1.6;">
                    <li style="margin-bottom:6px;">Harga saat ini <b>{int(harga):,}</b> berada <b style="color:{'#10B981' if dist_ma20 > 0 else '#EF4444'};">{abs(dist_ma20):.1f}% {'di atas' if dist_ma20 > 0 else 'di bawah'}</b> garis ekuilibrium jangka pendek (MA20: {int(ma20):,}).</li>
                    <li style="margin-bottom:6px;">Secara intraday, harga <b style="color:{'#10B981' if dist_vwap > 0 else '#EF4444'};">{abs(dist_vwap):.1f}% {'lebih tinggi' if dist_vwap > 0 else 'lebih rendah'}</b> dari rata-rata volume tertimbang bandar (VWAP: {int(vwap_val):,}). {'Dorongan beli sedang solid.' if dist_vwap > 0 else 'Waspada potensi tekanan jual lebih lanjut.'}</li>
                    <li>Batas pengamanan / <i>Stop Loss</i> krusial disarankan pada area <b>{int(s.get('TRAILING STOP', 0)):,}</b>. Disiplin *Cut Loss* jika harga *breakdown* dan ditutup (closing) di bawah level ini.</li>
                </ul>
            </div>
            """
            st.markdown(insight_html, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: PENGELOMPOKAN OTOMATIS
    # ------------------------------------------
    with tab_cluster:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>🎯 Kategori Pilihan Engine</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        
        if not df_all.empty:
            st.markdown("<div class='sop-title'>🟢 Sinyal Serok Bawah (Rebound)</div>", unsafe_allow_html=True)
            if 'SEROK_SIGNAL' in df_all.columns:
                df_serok = df_all[~df_all['SEROK_SIGNAL'].str.contains("TDK ADA", na=False)]
                if not df_serok.empty:
                    cols_serok = ['TICKER', 'HARGA', 'SEROK_SIGNAL', 'STATUS_BANDAR']
                    safe_cols_serok = [c for c in cols_serok if c in df_serok.columns]
                    st.dataframe(df_serok[safe_cols_serok], hide_index=True, use_container_width=True)
                else:
                    st.markdown("<div style='color:#71717A; font-size:12px; margin-bottom:15px;'>Belum ada saham yang masuk kriteria Serok Bawah saat ini.</div>", unsafe_allow_html=True)
                    
            st.markdown("<div class='sop-title' style='margin-top:20px;'>💰 Investasi Dividen (Yield >= 2%)</div>", unsafe_allow_html=True)
            if 'YIELD_RAW' in df_all.columns:
                df_div = df_all[df_all['YIELD_RAW'] >= 2.0].sort_values(by='YIELD_RAW', ascending=False)
                if not df_div.empty:
                    cols_div = ['TICKER', 'HARGA', 'YIELD', 'ROE', 'PBV', 'PER']
                    safe_cols_div = [c for c in cols_div if c in df_div.columns]
                    st.dataframe(df_div[safe_cols_div], hide_index=True, use_container_width=True)
                    
            st.markdown("<div class='sop-title' style='margin-top:20px;'>🐳 Aliran Uang Cerdas (Akumulasi)</div>", unsafe_allow_html=True)
            if 'STATUS_BANDAR' in df_all.columns:
                df_bandar = df_all[df_all['STATUS_BANDAR'].str.contains("AKUMULASI", na=False) | df_all['STATUS_BANDAR'].str.contains("MARK-UP", na=False)]
                if not df_bandar.empty:
                    cols_bandar = ['TICKER', 'HARGA', 'STATUS_BANDAR', 'WPI_SCORE']
                    safe_cols_bandar = [c for c in cols_bandar if c in df_bandar.columns]
                    st.dataframe(df_bandar[safe_cols_bandar], hide_index=True, use_container_width=True)
        else:
            st.info("Data kosong. Silakan lakukan SCAN terlebih dahulu.")

    # ------------------------------------------
    # TAB 3: EKSPOR & DAFTAR PANTAU
    # ------------------------------------------
    with tab_export:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>📥 Ekspor Data ke HP (Excel/CSV)</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        if not df_all.empty:
            cols_to_export = ['TICKER', 'NAME', 'HARGA', 'VWAP', 'AREA BELI', 'TRAILING STOP', 'FIBO_618', 'FIBO_500', 'SETUP_GRADE', 'SEROK_SIGNAL', 'STATUS_BANDAR', 'WPI_SCORE', 'ROE', 'PBV', 'YIELD', 'EPS']
            safe_export_cols = [c for c in cols_to_export if c in df_all.columns]
            df_export = df_all[safe_export_cols]
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 UNDUH DAFTAR PANTAUAN (CSV)",
                data=csv_data,
                file_name=f"JG_Ultimate_Watchlist_{get_waktu_wib().replace(':', '')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Lakukan SCAN terlebih dahulu di sidebar sebelum melakukan ekspor.")

    # ------------------------------------------
    # TAB 4 : SOP & PANDUAN PENGGUNAAN
    # ------------------------------------------
    with tab_sop:
        st.markdown("""
<div class="sop-box">
<div class="sop-title">Cara Penggunaan (SOP)</div>
<ol style="margin-left: -15px;">
<li>Buka sidebar (garis tiga di pojok kiri atas).</li>
<li>Pilih Timeframe yang diinginkan (Daily untuk Swing, Weekly untuk Investing).</li>
<li>Tekan tombol <b>🔄 SCAN</b> untuk mengumpulkan data terbaru dari market.</li>
<li>Buka Tab <b>DASHBOARD</b> untuk memantau 1 saham secara detail, atau buka Tab <b>CLUSTERING</b> untuk melihat saham pilihan algoritma secara massal.</li>
<li>Gunakan Tab <b>EXPORT</b> untuk menyimpan hasil scan ke HP Anda.</li>
</ol>
</div>

<div class="sop-box">
<div class="sop-title">Penjabaran Hasil Data Reel</div>
<ul style="margin-left: -15px; margin-bottom:0;">
<li style="margin-bottom:8px;"><b>Teknikal & MACD:</b> Menggunakan MA20 & MA50, diperkuat oleh MACD Golden Cross. Jika <i>Price > MA20</i> dan MACD Bullish, konfirmasi trend naik sangat kuat.</li>
<li style="margin-bottom:8px;"><b>WPI (Whale Pressure Index):</b> Indikator skor dari 0-100 yang mengukur seberapa kuat tekanan pembeli. Skor > 70 menunjukkan dominasi <i>buyer/bandar</i> yang kuat.</li>
<li style="margin-bottom:8px;"><b>Bandarmologi:</b> Menganalisa anomali Volume yang melonjak (Volume Spike) lalu dikawinkan dengan bentuk <i>Candlestick shadow</i>.</li>
<li style="margin-bottom:8px;"><b>Fundamental (ROE, PBV, EPS & YIELD):</b> <b>ROE</b> efisiensi laba (>10%), <b>PBV</b> valuasi saham (semakin rendah = murah), <b>EPS</b> adalah laba bersih per lembar saham, dan <b>YIELD</b> keuntungan dari Dividen rutin.</li>
<li style="margin-bottom:8px;"><b>Analyst Insights:</b> Data konsensus dari analis Wall Street yang menampilkan target proyeksi harga rata-rata institusi asing terhadap emiten tersebut.</li>
</ul>
</div>
""", unsafe_allow_html=True)
