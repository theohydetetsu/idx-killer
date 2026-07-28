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

warnings.filterwarnings('ignore')

# ==========================================
# 0. REACTIVE ENGINE & PERSISTENT CACHE (V18.0.0)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v18.json"

def load_reactive_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                loaded_stocks = cache_data.get("raw_stocks", [])
                ihsg_data = cache_data.get("ihsg", {"val": 0, "change": 0})
                if loaded_stocks and isinstance(loaded_stocks, list):
                    return loaded_stocks, cache_data.get("last_update", None), ihsg_data
        except: pass
    return [], None, {"val": 0, "change": 0}

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update, st.session_state.ihsg_data = load_reactive_cache()

if "reactive_mode" not in st.session_state: st.session_state.reactive_mode = False
if "current_tf" not in st.session_state: st.session_state.current_tf = "1 Hari (Daily)"

# ==========================================
# 1. LUXURY UI & EXTREME MOBILE CSS
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v18.0.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Background Onyx Black */
    [data-testid="stAppViewContainer"] { background-color: #050505 !important; color: #A1A1AA !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* Extreme Mobile precision padding */
    .block-container { 
        padding-top: 3.5rem !important; 
        padding-bottom: 1rem !important; 
        max-width: 100% !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important;
    }
    
    /* Ultra-Narrow Sidebar Luxury */
    section[data-testid="stSidebar"] { 
        background-color: #09090B !important; 
        border-right: 1px solid #1F1F22 !important; 
        min-width: 180px !important; 
        max-width: 180px !important;
    }
    section[data-testid="stSidebar"] * { color: #A1A1AA !important; }
    
    /* Styling Dropdown & Inputs */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #09090B !important;
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
        padding: 4px !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="input"] input {
        color: #FAFAFA !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Elegant Cards */
    .pro-card { 
        background: linear-gradient(145deg, #121214, #09090B);
        border: 1px solid #27272A; 
        border-radius: 10px; 
        padding: 14px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    .market-banner {
        background: linear-gradient(145deg, #18181B, #09090B);
        border: 1px solid #3F3F46;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Gold Accents */
    .card-label { color: #C6A87C; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 6px;}
    
    .header-profile { display: flex; justify-content: space-between; align-items: center; }
    .logo-circle { width: 42px; height: 42px; border-radius: 10px; background: linear-gradient(135deg, #C6A87C 0%, #8E793E 100%); display: flex; justify-content: center; align-items: center; font-size: 16px; font-weight: 800; color: #050505; margin-right: 12px;}
    .ticker-title { font-size: 24px; font-weight: 800; color: #FAFAFA; line-height: 1.1; display:flex; align-items:center; gap: 6px;}
    .ticker-desc { color: #A1A1AA; font-size: 12px; font-weight: 500; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px;}
    
    /* Refined Badges */
    .badge-primary { background: rgba(198, 168, 124, 0.1); color: #C6A87C; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(198, 168, 124, 0.3);}
    .badge-green { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
    .badge-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
    
    .score-box { background: #050505; border: 1px solid #27272A; border-radius: 8px; padding: 10px 14px; text-align: center; }
    .score-value { font-size: 32px; font-weight: 800; color: #C6A87C; line-height: 1; margin: 4px 0;}
    
    .data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;}
    .data-label { font-size: 10px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; display:block;}
    .data-value { font-size: 14px; color: #FAFAFA; font-weight: 700; display:block;}
    
    .meter-container { background: #27272A; height: 6px; border-radius: 3px; margin-top: 15px; position: relative;}
    .meter-fill { background: linear-gradient(90deg, #EF4444 0%, #C6A87C 50%, #10B981 100%); height: 100%; border-radius: 3px;}
    .meter-labels { display: flex; justify-content: space-between; font-size: 10px; color: #71717A; font-weight: 600; margin-top: 4px;}
    
    /* Tabs Overhaul */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 0px;}
    .stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 600; background: transparent; padding: 8px 6px; border: none; font-size: 12px;}
    .stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
    
    @media (max-width: 768px) {
        .ticker-title { font-size: 18px; }
        .ticker-desc { font-size: 11px; max-width: 140px; }
        .score-box { padding: 6px 10px; }
        .score-value { font-size: 24px; }
        .data-grid { grid-template-columns: 1fr 1fr !important; }
        .market-banner { flex-direction: column; text-align: center; gap: 6px; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE DATA FETCHING & INDICATORS
# ==========================================
MASTER_UNIVERSE = [
    "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT", "GOTO", "PGAS", "PTBA", "ITMG", 
    "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM", "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", 
    "SIDO", "MYOR", "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR", "TBIG", "MTEL", 
    "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS", "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", 
    "DOID", "HRUM", "INCO", "PTMP", "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE", 
    "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH", "CLEO", "CMRY", "SILO", "MIKA", 
    "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA", "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", 
    "AALI", "SSMS", "BBYB", "AGRO", "ARKA", "TOTO", "MLBI", "INDY", "PTRO", "MBAP", "BSSR", "SMMT", "KKGI", "ABMM", 
    "CFIN", "MFIN", "ADMF", "BBKP", "PNBN", "BNLI", "SAGE", "GZCO", "STRK", "WIFI", "AEGS", "GOLF", "FILM", "ELSA",
    "RAJA", "HATM", "KRYA", "BSBK", "DATA", "NICL", "PAMG", "TRJA", "CARS", "BAPA", "KIJA", "DILD", "LPCK"
]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M")

def fetch_ihsg():
    try:
        tkr = yf.Ticker("^JKSE")
        hist = tkr.history(period="5d")
        if len(hist) >= 2:
            now = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            change = ((now - prev) / prev) * 100
            return {"val": now, "change": change}
    except: pass
    return {"val": 0, "change": 0}

def get_dynamic_market_roster():
    try:
        df_batch = yf.download(master_tickers, period="5d", group_by="ticker", threads=True, progress=False)
        market_data = []
        for ticker in master_tickers:
            try:
                if isinstance(df_batch.columns, pd.MultiIndex): df_t = df_batch[ticker].dropna()
                else: df_t = df_batch.dropna()
                if len(df_t) < 2: continue
                close_now, close_prev, vol_now = float(df_t['Close'].iloc[-1]), float(df_t['Close'].iloc[-2]), float(df_t['Volume'].iloc[-1])
                if close_now < 50: continue 
                
                # UPGRADE 1: Filter Likuiditas (ADTV > 3 Miliar)
                adtv = close_now * vol_now
                pct_change = ((close_now - close_prev) / close_prev) * 100
                market_data.append({'Ticker': ticker, 'Change': pct_change, 'TransVal': adtv, 'VolatilityScore': abs(pct_change) * adtv})
            except: continue
            
        df_market = pd.DataFrame(market_data)
        # Saring ketat: HANYA yang transaksi hariannya > 3 Miliar Rupiah
        df_market = df_market[df_market['TransVal'] >= 3_000_000_000]
        
        if df_market.empty: return master_tickers[:100] 
        top_gainers = df_market.nlargest(100, 'Change')['Ticker'].tolist()
        top_liquid = df_market.nlargest(100, 'TransVal')['Ticker'].tolist()
        return list(set(top_gainers + top_liquid))[:200]
    except: return master_tickers[:100] 

def hitung_rsi(df, periods=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/periods, min_periods=periods).mean()
    loss = (-1 * delta.clip(upper=0)).ewm(alpha=1/periods, min_periods=periods).mean()
    return 100 - (100 / (1 + (gain / loss)))

def hitung_stochastic(df, k_period=14, d_period=3):
    low_min, high_max = df['Low'].rolling(window=k_period).min(), df['High'].rolling(window=k_period).max()
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min + 1e-9))
    return stoch_k, stoch_k.rolling(window=d_period).mean()

def hitung_atr(df, period=14):
    high_low, high_close, low_close = df['High'] - df['Low'], np.abs(df['High'] - df['Close'].shift()), np.abs(df['Low'] - df['Close'].shift())
    return np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1).rolling(period).mean()

def fetch_single_stock(emiten, mode_tf):
    try:
        per, inv = "1y", "1d" 
        kode = emiten.replace(".JK", "")
        tkr = yf.Ticker(emiten)
        df = tkr.history(period=per, interval=inv)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
        df = df.ffill().dropna(subset=['Close'])
        if len(df) < 30: return None 
        
        # Calculate Base Indicators
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = hitung_rsi(df)
        df['Stoch_K'], df['Stoch_D'] = hitung_stochastic(df)
        df['ATR'] = hitung_atr(df)
        df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Chandelier_Exit'] = df['High'].rolling(22).max() - (df['ATR'] * 3.0)
        df['Turnover'] = df['Close'] * df['Volume']
        
        df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        macd_bullish = float(df['MACD'].iloc[-1]) > float(df['Signal_Line'].iloc[-1])
        
        harga_skg = float(df['Close'].iloc[-1])
        open_skg = float(df['Open'].iloc[-1])
        high_skg = float(df['High'].iloc[-1])
        low_skg = float(df['Low'].iloc[-1])
        vol_skg = float(df['Volume'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        ema20_skg = float(df['EMA20'].iloc[-1])
        sma50_skg = float(df['SMA50'].iloc[-1])
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        adtv_20 = float(df['Turnover'].rolling(20).mean().iloc[-1])
        
        is_bullish = harga_skg >= open_skg
        body_size = abs(open_skg - harga_skg)
        lower_shadow = (open_skg if is_bullish else harga_skg) - low_skg
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        
        is_vol_spike = vol_skg > (vol_sma20 * 1.5)
        
        # UPGRADE 2: Bull Trap & Strict Bandarmology
        is_bull_trap = is_vol_spike and (upper_shadow > body_size * 1.5) and not is_bullish
        is_fake_pump = is_vol_spike and (upper_shadow > body_size * 2) and is_bullish
        
        low_20 = float(df['Low'].tail(20).min())
        is_near_bottom = (harga_skg - low_20) / low_20 <= 0.08
        
        if is_bull_trap or is_fake_pump: status_bandar = "🚨 BULL TRAP / DISTRIBUSI"
        elif is_vol_spike and lower_shadow > (body_size * 1.5) and is_near_bottom: status_bandar = "🐋 AKUMULASI DASAR"
        elif is_vol_spike and is_bullish and upper_shadow < body_size: status_bandar = "🚀 MARK-UP SOLID"
        elif is_vol_spike and not is_bullish: status_bandar = "🩸 DISTRIBUSI MASIF"
        else: status_bandar = "➖ NEUTRAL"

        if (float(df['Stoch_K'].iloc[-1]) < 25) and is_near_bottom and not is_bull_trap: serok_signal = "🟢 OVERSOLD REBOUND"
        elif "AKUMULASI DASAR" in status_bandar: serok_signal = "🐋 WHALE ABSORPTION"
        else: serok_signal = "➖ TDK ADA"

        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        if is_bull_trap or is_fake_pump: wpi_score = max(0, wpi_score - 40) # Penalty score
        
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg: trailing_stop = harga_skg - (float(df['ATR'].iloc[-1]) * 2) 
        
        # Strict Setup Grade
        setup_score = sum([harga_skg > ema20_skg, wpi_score > 70, vol_skg > vol_sma20, "TDK ADA" not in serok_signal, macd_bullish])
        if "BULL TRAP" in status_bandar or "DISTRIBUSI" in status_bandar: setup_grade = "☠️ HINDARI (DISTRIBUSI)"
        elif adtv_20 < 3_000_000_000: setup_grade = "⚠️ ILLIQUID / GORENGAN"
        elif setup_score >= 4 and wpi_score >= 70: setup_grade = "⭐ SETUP A+ (Aman)"
        elif setup_score >= 3: setup_grade = "✔️ SETUP B (Speculative)"
        else: setup_grade = "⏳ WAIT / WATCHLIST"

        info = tkr.info if hasattr(tkr, 'info') and tkr.info else {}
        return {
            "TICKER": kode, "HARGA": harga_skg, "MA20": ema20_skg, "MA50": sma50_skg, 
            "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3), 
            "TRAILING STOP": trailing_stop, "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal, "STATUS_BANDAR": status_bandar, "SETUP_GRADE": setup_grade, 
            "PER": round(info.get('trailingPE', 0.0), 2) if info.get('trailingPE') else 0.0, 
            "ROE": round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 0.0,
            "YIELD": f"{round(info.get('dividendYield', 0)*100, 2) if info.get('dividendYield') else 0}%", 
            "PBV": round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else 0.0, 
            "EPS": float(info.get('trailingEps', 0.0)),
            "RET_1D": ((harga_skg - prev_close) / prev_close * 100), "VOLUME": vol_skg, "VOL_SMA20": vol_sma20, 
            "ATR_PCT": (float(df['ATR'].iloc[-1]) / harga_skg) * 100, "NAME": info.get('longName', kode),
            "SECTOR": info.get('sector', 'Sektor Tidak Tersedia'), "INDUSTRY": info.get('industry', 'Industri Tidak Tersedia'),
            "MACD_BULLISH": macd_bullish, "ADTV_20": adtv_20
        }
    except Exception as e: return None

# ==========================================
# 3. SIDEBAR (ULTRA-NARROW LUXURY)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#C6A87C; font-size:16px; font-weight:800; margin-bottom:0;'>🛡️ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#71717A; font-size:9px; letter-spacing:1px; margin-bottom:20px;'>DEFENSIVE V18.0.0</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:10px; color:#A1A1AA; margin-bottom:5px;'>⏱️ Timeframe:</div>", unsafe_allow_html=True)
    tf_pilihan = st.selectbox("TF", ("1 Hari (Daily)", "1 Minggu (Weekly)"), index=0, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='color:#FAFAFA; font-size:10px; font-weight:700; margin-bottom:5px;'>⚙️ AUTO-SYNC</div>", unsafe_allow_html=True)
    reactive_on = st.toggle("Live Mode", value=st.session_state.reactive_mode)
    if reactive_on != st.session_state.reactive_mode:
        st.session_state.reactive_mode = reactive_on
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 SCAN MARKET", use_container_width=True):
        st.session_state.raw_stocks = []
        
        radar_bar_ihsg = st.progress(0, text="Membaca IHSG & Likuiditas...")
        st.session_state.ihsg_data = fetch_ihsg()
        dynamic_tickers = get_dynamic_market_roster()
        radar_bar_ihsg.empty()
        
        my_bar = st.progress(0, text=f"Scanning Protokol Keamanan...")
        for i, t in enumerate(dynamic_tickers):
            my_bar.progress((i + 1) / len(dynamic_tickers), text=f"{t} ({i+1}/{len(dynamic_tickers)})")
            data = fetch_single_stock(t, tf_pilihan)
            if data: st.session_state.raw_stocks.append(data)
            gc.collect() 
        my_bar.empty()
        st.session_state.last_update = get_waktu_wib()
        try:
            with open(CACHE_FILE, "w") as f: 
                json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update, "ihsg": st.session_state.ihsg_data}, f)
        except: pass
        st.rerun()
        
    if st.session_state.last_update:
        st.markdown(f"<div style='font-size:8px; color:#71717A; text-align:center; margin-top:20px;'>Last Update:<br>{st.session_state.last_update}</div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN TABS
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN MARKET' di sidebar untuk memulai deteksi.")
else:
    tab_dash, tab_cluster, tab_export = st.tabs(["✨ DASHBOARD & RISK", "🎯 CLUSTER AMAN", "📥 EXPORT"])
    
    # ------------------------------------------
    # TAB 1: LUXURY DASHBOARD & RISK CALCULATOR
    # ------------------------------------------
    with tab_dash:
        ihsg = st.session_state.ihsg_data
        ihsg_val, ihsg_change = ihsg.get("val", 0), ihsg.get("change", 0)
        
        market_banner_html = f"""
<div class="market-banner">
<div>
<div style="font-size:10px; color:#A1A1AA; text-transform:uppercase; font-weight:700;">🇲🇨 IHSG (COMPOSITE)</div>
<div style="font-size:18px; font-weight:800; color:{'#10B981' if ihsg_change >= 0 else '#EF4444'}; margin-top:2px;">{ihsg_val:,.2f} <span style="font-size:12px;">({'+' if ihsg_change>=0 else ''}{ihsg_change:.2f}%)</span></div>
</div>
</div>
"""
        st.markdown(market_banner_html, unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px; color:#71717A; font-weight:700; margin-bottom:5px;'>🔍 CARI EMITEN (YANG SUDAH LOLOS FILTER LIKUIDITAS)</div>", unsafe_allow_html=True)
        pilihan_ticker = st.selectbox("Pilih", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0, label_visibility="collapsed")
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            grade = s.get("SETUP_GRADE", "WAIT")
            volatility_badge = "HIGH RISK" if s.get('ATR_PCT', 0) > 4 else "NORMAL"
            
            if "A+" in grade: action_text, action_color, action_bg = "BUY (AMAN)", "#10B981", "rgba(16, 185, 129, 0.1)"
            elif "HINDARI" in grade or "ILLIQUID" in grade: action_text, action_color, action_bg = "🚨 DANGER / JANGAN BELI", "#EF4444", "rgba(239, 68, 68, 0.1)"
            else: action_text, action_color, action_bg = "WAIT / WATCHLIST", "#C6A87C", "rgba(198, 168, 124, 0.1)"
                
            status_bandar = s.get('STATUS_BANDAR', 'NEUTRAL')
            serok_sig = s.get('SEROK_SIGNAL', '➖ TDK ADA').split()[0]
            harga, ma20, ma50 = s.get('HARGA', 0), s.get('MA20', 0), s.get('MA50', 0)
            sl_price = s.get('TRAILING STOP', 0)
            
            html_header = f"""
<div class="pro-card">
<div class="header-profile">
<div style="display:flex; align-items:center;">
<div class="logo-circle">{s.get('TICKER', 'XX')[:2]}</div>
<div>
<div class="ticker-title">{s.get('TICKER', '')} <span class="badge-primary">V18.0.0</span></div>
<div class="ticker-desc">{s.get('NAME', '')}</div>
<div style="color:#C6A87C; font-size:10px; font-weight:600; margin-top:2px;">{s.get('SECTOR', 'Unknown')}</div>
</div>
</div>
<div class="score-box">
<div style="font-size:9px; color:#71717A; text-transform:uppercase; font-weight:700;">WPI Score</div>
<div class="score-value" style="color: {'#EF4444' if s.get('WPI_SCORE', 0) < 40 else '#C6A87C'};">{s.get('WPI_SCORE', 0):.1f}</div>
</div>
</div>
</div>
"""
            st.markdown(html_header, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1.5, 1])
            with col1:
                bandar_color = '#EF4444' if 'DISTRIBUSI' in status_bandar or 'TRAP' in status_bandar else ('#10B981' if 'AKUMULASI' in status_bandar or 'MARK-UP' in status_bandar else '#C6A87C')
                html_col1 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">⚡ RINGKASAN STRATEGI & BANDARMOLOGI</div>
<div style="display:flex; justify-content:space-between; border-bottom: 1px solid #27272A; padding-bottom: 8px;">
<div>
<span class="data-label">ADTV 20D (LIKUIDITAS)</span>
<span class="data-value" style="font-size:13px; color:{'#10B981' if s.get('ADTV_20',0) > 10000000000 else '#C6A87C'};">Rp {s.get('ADTV_20', 0)/1e9:.1f} Miliar/Hari</span>
</div>
<div style="text-align:right;">
<span class="data-label">BANDAR FLOW</span>
<span class="data-value" style="font-size:13px; color: {bandar_color};">{status_bandar}</span>
</div>
</div>
<div class="meter-container">
<div class="meter-fill" style="width: {s.get('WPI_SCORE', 0)}%;"></div>
</div>
</div>
"""
                st.markdown(html_col1, unsafe_allow_html=True)
                
            with col2:
                html_col2 = f"""
<div class="pro-card" style="height:100%; text-align:center;">
<div class="card-label" style="justify-content:center; border:none; margin-bottom:2px;">🎯 STATUS SETUP AI</div>
<div style="background: {action_bg}; border: 1px solid {action_color}; border-radius: 8px; padding: 10px; margin-top: 8px;">
<div style="color: {action_color}; font-size: 15px; font-weight: 800;">{grade}</div>
</div>
</div>
"""
                st.markdown(html_col2, unsafe_allow_html=True)

            # UPGRADE 3: RISK MANAGEMENT CALCULATOR (SOP)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="pro-card" style="border-left: 4px solid #3B82F6;">
            <div class="card-label" style="color:#3B82F6;">🛡️ SOP KALKULATOR MANAJEMEN RISIKO (WAJIB ISI SEBELUM BELI)</div>
            <p style="font-size:12px; color:#A1A1AA; margin-bottom:15px;">Mencegah porto berdarah. Hitung otomatis batas maksimal Lot yang boleh dibeli berdasarkan toleransi kerugian modal Anda.</p>
            """, unsafe_allow_html=True)
            
            calc_c1, calc_c2 = st.columns(2)
            with calc_c1:
                modal_rp = st.number_input("💰 Total Modal Portofolio (Rp)", min_value=1000000, value=10000000, step=1000000)
            with calc_c2:
                risk_pct = st.number_input("📉 Toleransi Cut Loss dari Modal (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5, help="Standar aman: 1% - 2% dari total modal.")
            
            # Perhitungan Lot
            risk_amount = modal_rp * (risk_pct / 100)
            jarak_sl_rp = harga - sl_price
            
            if jarak_sl_rp > 0:
                jarak_sl_pct = (jarak_sl_rp / harga) * 100
                max_lembar = risk_amount / jarak_sl_rp
                max_lot = int(max_lembar / 100)
                total_beli_rp = max_lot * 100 * harga
                
                st.markdown(f"""
                <div style="background: #09090B; border: 1px solid #27272A; border-radius: 8px; padding: 15px; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #27272A; padding-bottom: 10px; margin-bottom: 10px;">
                        <div>
                            <span style="font-size:10px; color:#71717A; font-weight:700;">Harga Beli (Sekarang)</span><br>
                            <span style="font-size:16px; color:#FAFAFA; font-weight:800;">Rp {int(harga):,}</span>
                        </div>
                        <div style="text-align:center;">
                            <span style="font-size:10px; color:#71717A; font-weight:700;">Titik Cut Loss Mutlak</span><br>
                            <span style="font-size:16px; color:#EF4444; font-weight:800;">Rp {int(sl_price):,} (-{jarak_sl_pct:.1f}%)</span>
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <span style="font-size:11px; color:#C6A87C; font-weight:700; text-transform:uppercase;">Maksimal Lot Yang Boleh Dibeli:</span><br>
                        <span style="font-size:36px; color:#3B82F6; font-weight:800;">{max_lot:,} LOT</span><br>
                        <span style="font-size:12px; color:#A1A1AA;">(Senilai Rp {int(total_beli_rp):,})</span>
                    </div>
                    <div style="margin-top:10px; font-size:11px; color:#EF4444; text-align:center; background:rgba(239, 68, 68, 0.1); padding:8px; border-radius:4px;">
                        Jika harga turun menyentuh Stop Loss, kerugian maksimal Anda <b>PASTI HANYA Rp {int(risk_amount):,}</b> ({risk_pct}% dari modal).
                    </div>
                </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 8px; padding: 15px; margin-top: 10px; text-align:center;">
                <span style="color:#EF4444; font-weight:700;">🚨 HARGA SAAT INI SUDAH DI BAWAH BATAS STOP LOSS! JANGAN MEMBELI SAHAM INI!</span>
                </div></div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: CLUSTERING (SAFE ZONE)
    # ------------------------------------------
    with tab_cluster:
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        if not df_all.empty:
            st.markdown("<h4 style='color:#10B981; font-size:14px; margin-bottom:15px;'>🛡️ Daftar Saham Aman (Lolos Filter Anti-Gorengan)</h4>", unsafe_allow_html=True)
            
            df_aman = df_all[df_all['ADTV_20'] >= 3_000_000_000]
            df_aman = df_aman[~df_aman['STATUS_BANDAR'].str.contains("BULL TRAP|DISTRIBUSI", na=False)]
            
            if not df_aman.empty:
                cols_show = ['TICKER', 'HARGA', 'STATUS_BANDAR', 'SETUP_GRADE', 'WPI_SCORE']
                safe_cols = [c for c in cols_show if c in df_aman.columns]
                st.dataframe(df_aman[safe_cols], hide_index=True, use_container_width=True)
            else:
                st.markdown("<div style='color:#71717A; font-size:12px;'>Market sedang hancur. Tidak ada saham yang lolos filter keamanan hari ini.</div>", unsafe_allow_html=True)
        else:
            st.info("Data kosong. Silakan lakukan SCAN terlebih dahulu.")

    # ------------------------------------------
    # TAB 3: EXPORT
    # ------------------------------------------
    with tab_export:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>📥 Ekspor Watchlist</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        if not df_all.empty:
            df_export = df_all[['TICKER', 'NAME', 'HARGA', 'AREA BELI', 'TRAILING STOP', 'SETUP_GRADE', 'STATUS_BANDAR']]
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 DOWNLOAD WATCHLIST", data=csv_data, file_name=f"JG_Ultimate_V18_{get_waktu_wib().replace(':', '')}.csv", mime="text/csv", use_container_width=True)
        else:
            st.warning("Lakukan SCAN MARKET terlebih dahulu.")
