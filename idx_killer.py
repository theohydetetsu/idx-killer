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
# 0. REACTIVE ENGINE & PERSISTENT CACHE (V17.7)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v177.json"

def load_reactive_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                loaded_stocks = cache_data.get("raw_stocks", [])
                if loaded_stocks and isinstance(loaded_stocks, list):
                    return loaded_stocks, cache_data.get("last_update", None)
        except: pass
    return [], None

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update = load_reactive_cache()

if "reactive_mode" not in st.session_state: st.session_state.reactive_mode = False
if "current_tf" not in st.session_state: st.session_state.current_tf = "1 Hari (Daily)"

# ==========================================
# 1. LUXURY UI & EXTREME MOBILE CSS
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v17.7", page_icon="✨", layout="wide")

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
    
    /* Styling Dropdown */
    div[data-baseweb="select"] > div {
        background-color: #09090B !important;
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
        padding: 4px !important;
    }
    div[data-baseweb="select"] span {
        color: #FAFAFA !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Elegant Cards */
    .pro-card { 
        background: linear-gradient(145deg, #121214, #09090B);
        border: 1px solid #27272A; 
        border-radius: 10px; 
        padding: 12px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    /* Gold Accents */
    .card-label { color: #C6A87C; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 6px;}
    
    .header-profile { display: flex; justify-content: space-between; align-items: center; }
    .logo-circle { width: 40px; height: 40px; border-radius: 10px; background: linear-gradient(135deg, #C6A87C 0%, #8E793E 100%); display: flex; justify-content: center; align-items: center; font-size: 16px; font-weight: 800; color: #050505; margin-right: 12px;}
    .ticker-title { font-size: 22px; font-weight: 800; color: #FAFAFA; line-height: 1.1; display:flex; align-items:center; gap: 6px;}
    .ticker-desc { color: #A1A1AA; font-size: 11px; font-weight: 500; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px;}
    
    /* Refined Badges */
    .badge-primary { background: rgba(198, 168, 124, 0.1); color: #C6A87C; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; border: 1px solid rgba(198, 168, 124, 0.3);}
    .badge-green { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
    .badge-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
    
    .score-box { background: #050505; border: 1px solid #27272A; border-radius: 8px; padding: 8px 12px; text-align: center; }
    .score-value { font-size: 20px; font-weight: 800; color: #C6A87C; line-height: 1; margin: 4px 0;}
    
    .data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;}
    .data-label { font-size: 9px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; display:block;}
    .data-value { font-size: 13px; color: #FAFAFA; font-weight: 700; display:block;}
    
    .meter-container { background: #27272A; height: 5px; border-radius: 3px; margin-top: 15px; position: relative;}
    .meter-fill { background: linear-gradient(90deg, #EF4444 0%, #C6A87C 50%, #10B981 100%); height: 100%; border-radius: 3px;}
    .meter-labels { display: flex; justify-content: space-between; font-size: 9px; color: #71717A; font-weight: 600; margin-top: 4px;}
    
    /* Tabs Overhaul */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 5px;}
    .stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 600; background: transparent; padding: 8px 10px; border: none; font-size:12px;}
    .stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
    
    .sop-box { background: #09090B; border-left: 3px solid #C6A87C; padding: 12px; margin-bottom: 15px; font-size: 12px; color: #D4D4D8; line-height:1.6;}
    .sop-title { color: #C6A87C; font-weight: 700; font-size: 14px; margin-bottom: 8px; text-transform: uppercase;}
    
    @media (max-width: 768px) {
        .header-profile { flex-direction: column; text-align: center; gap: 8px; }
        .logo-circle { margin: 0 auto; }
        .ticker-title { justify-content: center; flex-wrap: wrap;}
        .ticker-desc { max-width: 100%; }
        .data-grid { grid-template-columns: 1fr 1fr !important; }
        .score-box { width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE DATA FETCHING & INDICATORS
# ==========================================
MASTER_UNIVERSE = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT", "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM", "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR", "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR", "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS", "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP", "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE", "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH", "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA", "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS", "BBYB", "AGRO", "ARKA"]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M")

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
                if close_now < 50 or vol_now < 100000: continue 
                pct_change = ((close_now - close_prev) / close_prev) * 100
                trans_val = close_now * vol_now
                market_data.append({'Ticker': ticker, 'Change': pct_change, 'TransVal': trans_val, 'VolatilityScore': abs(pct_change) * trans_val})
            except: continue
        df_market = pd.DataFrame(market_data)
        if df_market.empty: return master_tickers[:150] 
        top_gainers = df_market.nlargest(60, 'Change')['Ticker'].tolist()
        top_liquid = df_market.nlargest(50, 'TransVal')['Ticker'].tolist()
        top_volatile = df_market.nlargest(40, 'VolatilityScore')['Ticker'].tolist()
        return list(set(top_gainers + top_liquid + top_volatile))[:150]
    except: return master_tickers[:150] 

def hitung_rsi(df, periods=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/periods, min_periods=periods).mean()
    loss = (-1 * delta.clip(upper=0)).ewm(alpha=1/periods, min_periods=periods).mean()
    return 100 - (100 / (1 + (gain / loss)))

def hitung_stochastic(df, k_period=14, d_period=3):
    low_min, high_max = df['Low'].rolling(window=k_period).min(), df['High'].rolling(window=k_period).max()
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min + 1e-9))
    return stoch_k, stoch_k.rolling(window=d_period).mean()

def check_bullish_divergence(df, window=20):
    try:
        recent = df.tail(window)
        if len(recent) < window: return False
        p_min1_idx, p_min2_idx = recent['Low'].iloc[:-5].idxmin(), recent['Low'].iloc[-5:].idxmin()
        if (recent.loc[p_min2_idx, 'Low'] < recent.loc[p_min1_idx, 'Low']) and (recent.loc[p_min2_idx, 'RSI'] > recent.loc[p_min1_idx, 'RSI']): return True
    except: pass
    return False

def hitung_atr(df, period=14):
    high_low, high_close, low_close = df['High'] - df['Low'], np.abs(df['High'] - df['Close'].shift()), np.abs(df['Low'] - df['Close'].shift())
    return np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1).rolling(period).mean()

def fetch_single_stock(emiten, mode_tf):
    try:
        per, inv = "1y", "1d" 
        kode = emiten.replace(".JK", "")
        df = yf.download(emiten, period=per, interval=inv, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
        df = df.ffill().dropna(subset=['Close'])
        if len(df) < 30: return None 
        
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = hitung_rsi(df)
        df['Stoch_K'], df['Stoch_D'] = hitung_stochastic(df)
        df['ATR'] = hitung_atr(df)
        df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Chandelier_Exit'] = df['High'].rolling(22).max() - (df['ATR'] * 3.0)
        
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

        if has_bullish_div and is_near_bottom: serok_signal = "🎯 BULLISH DIVERGENCE"
        elif is_whale_absorption: serok_signal = "🐋 WHALE ABSORPTION"
        elif (float(df['Stoch_K'].iloc[-1]) < 30) and (float(df['Stoch_K'].iloc[-1]) > float(df['Stoch_D'].iloc[-1])) and is_near_bottom: serok_signal = "🟢 OVERSOLD REBOUND"
        else: serok_signal = "➖ TDK ADA"

        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg: trailing_stop = harga_skg - (float(df['ATR'].iloc[-1]) * 2) 
        
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        is_vol_spike = vol_skg > (vol_sma20 * 1.2)
        if is_vol_spike:
            if lower_shadow > (body_size * 1.5): status_bandar = "🐋 AKUMULASI DASAR"
            elif upper_shadow > (body_size * 1.5): status_bandar = "🩸 DISTRIBUSI PUCUK"
            elif is_bullish and wpi_score > 70: status_bandar = "🚀 MARK-UP BERINGAS"
            elif is_bullish: status_bandar = "🟢 AKUMULASI AWAL"
            else: status_bandar = "💥 MARK-DOWN"
        else: status_bandar = "➖ NEUTRAL"
            
        setup_score = sum([harga_skg > ema20_skg, wpi_score > 85, vol_skg > vol_sma20*2, "TDK ADA" not in serok_signal])
        if "TDK ADA" not in serok_signal: setup_grade = "🎯 SETUP JACKPOT"
        elif setup_score >= 2 and wpi_score >= 70: setup_grade = "⭐ SETUP A+"
        elif setup_score >= 1 and wpi_score >= 80: setup_grade = "⚡ SETUP AGGRESSIVE"
        elif setup_score >= 1: setup_grade = "✔️ SETUP B"
        else: setup_grade = "⚠️ WAIT/WATCHLIST"

        tkr = yf.Ticker(emiten)
        info = tkr.info if tkr.info else {}
        
        # FIX LOGIC DIVIDEND YIELD AGAR NORMAL & PRESISI (Menghindari nilai ribuan)
        raw_yield = info.get('dividendYield', 0)
        if raw_yield is None:
            div_yield = 0.0
        elif raw_yield > 1.0: 
            div_yield = round(raw_yield, 2)
        else:
            div_yield = round(raw_yield * 100, 2)
            
        market_cap = info.get('marketCap', 0)
        
        return {
            "TICKER": kode, "HARGA": harga_skg, "MA20": ema20_skg, "MA50": sma50_skg, 
            "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3), 
            "TRAILING STOP": trailing_stop, "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal, "STATUS_BANDAR": status_bandar, "SETUP_GRADE": setup_grade, 
            "PER": round(info.get('trailingPE', 0.0), 2), "ROE": round(info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0, 2),
            "YIELD": f"{div_yield}%", "YIELD_RAW": div_yield, "MCAP": market_cap,
            "RET_1D": ((harga_skg - prev_close) / prev_close * 100), "VOLUME": vol_skg, "VOL_SMA20": vol_sma20, 
            "ATR_PCT": (float(df['ATR'].iloc[-1]) / harga_skg) * 100, "NAME": info.get('longName', kode)
        }
    except Exception as e: return None

# ==========================================
# 3. SIDEBAR (ULTRA-NARROW LUXURY)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#C6A87C; font-size:16px; font-weight:800; margin-bottom:0;'>✨ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#71717A; font-size:9px; letter-spacing:1px; margin-bottom:20px;'>EDITION V17.7</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:10px; color:#A1A1AA; margin-bottom:5px;'>⏱️ Timeframe:</div>", unsafe_allow_html=True)
    tf_pilihan = st.selectbox("TF", ("1 Hari (Daily)", "1 Minggu (Weekly)"), index=0, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='color:#FAFAFA; font-size:10px; font-weight:700; margin-bottom:5px;'>⚙️ AUTO-SYNC</div>", unsafe_allow_html=True)
    reactive_on = st.toggle("Live Mode", value=st.session_state.reactive_mode)
    if reactive_on != st.session_state.reactive_mode:
        st.session_state.reactive_mode = reactive_on
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 SCAN", use_container_width=True):
        st.session_state.raw_stocks = []
        radar_bar = st.progress(0, text="Mendeteksi Saham...")
        dynamic_tickers = get_dynamic_market_roster()
        radar_bar.empty()
        
        my_bar = st.progress(0, text=f"Scanning...")
        for i, t in enumerate(dynamic_tickers):
            my_bar.progress((i + 1) / len(dynamic_tickers), text=f"{t} ({i+1}/{len(dynamic_tickers)})")
            data = fetch_single_stock(t, tf_pilihan)
            if data: st.session_state.raw_stocks.append(data)
            gc.collect() 
        my_bar.empty()
        st.session_state.last_update = get_waktu_wib()
        try:
            with open(CACHE_FILE, "w") as f: 
                json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update}, f)
        except: pass
        st.rerun()
        
    if st.session_state.last_update:
        st.markdown(f"<div style='font-size:8px; color:#71717A; text-align:center; margin-top:20px;'>Last Update:<br>{st.session_state.last_update}</div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN TABS (DASHBOARD, CLUSTERING, SOP)
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN' di sidebar untuk memulai.")
else:
    tab_dash, tab_cluster, tab_sop = st.tabs(["✨ DASHBOARD", "🎯 CLUSTERING", "📖 SOP & PANDUAN"])
    
    # ------------------------------------------
    # TAB 1: LUXURY DASHBOARD
    # ------------------------------------------
    with tab_dash:
        st.markdown("<div style='font-size:10px; color:#71717A; font-weight:700; margin-bottom:5px; text-transform:uppercase;'>🔍 Cari Emiten</div>", unsafe_allow_html=True)
        pilihan_ticker = st.selectbox("Pilih", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0, label_visibility="collapsed")
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            grade = s.get("SETUP_GRADE", "WAIT")
            atr_pct = s.get('ATR_PCT', 0)
            volatility_badge = "HIGH" if atr_pct > 4 else "NORMAL"
            
            if "JACKPOT" in grade or "A+" in grade:
                action_text, action_color, action_bg = "BUY / ACCUMULATE", "#10B981", "rgba(16, 185, 129, 0.1)"
            elif "WAIT" in grade:
                action_text, action_color, action_bg = "WAIT / WATCHLIST", "#C6A87C", "rgba(198, 168, 124, 0.1)"
            else:
                action_text, action_color, action_bg = "SPECULATIVE BUY", "#FAFAFA", "rgba(250, 250, 250, 0.1)"
                
            vol, vol_sma = s.get('VOLUME', 0), s.get('VOL_SMA20', 1)
            status_bandar = s.get('STATUS_BANDAR', 'NEUTRAL')
            serok_sig = s.get('SEROK_SIGNAL', '➖ TDK ADA').split()[0]
            harga, ma20, ma50 = s.get('HARGA', 0), s.get('MA20', 0), s.get('MA50', 0)
            
            html_header = f"""
<div class="pro-card">
<div class="header-profile">
<div style="display:flex; align-items:center;">
<div class="logo-circle">{s.get('TICKER', 'XX')[:2]}</div>
<div>
<div class="ticker-title">{s.get('TICKER', '')} <span class="badge-primary">V17.7</span></div>
<div class="ticker-desc">{s.get('NAME', '')}</div>
</div>
</div>
<div class="score-box">
<div style="font-size:8px; color:#71717A; letter-spacing:1px; text-transform:uppercase;">WPI Score</div>
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
<div class="card-label">⚡ RINGKASAN STRATEGI</div>
<div style="display:flex; justify-content:space-between; border-bottom: 1px solid #27272A; padding-bottom: 8px;">
<div>
<span class="data-label">FUNDAMENTAL</span>
<span class="data-value">ROE <span style="color:#C6A87C;">{s.get('ROE', 0)}%</span> | YIELD <span style="color:#C6A87C;">{s.get('YIELD', '0%')}</span></span>
</div>
<div style="text-align:right;">
<span class="data-label">BANDAR FLOW</span>
<span class="data-value" style="color: {'#10B981' if 'AKUMULASI' in status_bandar else '#C6A87C' if 'NEUTRAL' in status_bandar else '#EF4444'};">{status_bandar}</span>
</div>
</div>
<div class="meter-container">
<div class="meter-fill" style="width: {s.get('WPI_SCORE', 0)}%;"></div>
</div>
<div class="meter-labels">
<span>BEARISH</span><span>NEUTRAL</span><span>BULLISH</span>
</div>
</div>
"""
                st.markdown(html_col1, unsafe_allow_html=True)
                
            with col2:
                html_col2 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">🌐 SMART MONEY</div>
<div style="text-align:center; margin: 5px 0;">
<div style="font-size:22px; font-weight:800; color:{'#10B981' if vol > vol_sma else '#A1A1AA'};">
{vol/1000000:.1f}M
</div>
<div class="badge-{'green' if vol > vol_sma else 'red'}" style="display:inline-block; margin-top:2px;">
{'VOLUME SPIKE' if vol > vol_sma else 'VOLUME DRY'}
</div>
</div>
<div style="text-align:center; font-size:10px; font-weight:600; margin-top:8px; border-top: 1px solid #27272A; padding-top:6px; color:#EF4444;">
SIG: {serok_sig}
</div>
</div>
"""
                st.markdown(html_col2, unsafe_allow_html=True)
                
            col3, col4 = st.columns([1.5, 1])
            with col3:
                cond_price = "badge-green" if harga > ma20 else "badge-red"
                cond_ma = "badge-green" if ma20 > ma50 else "badge-red"
                html_col3 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">📈 KONDISI HARGA</div>
<div class="data-grid">
<div><span class="data-label">LAST PRICE</span><span class="data-value">{int(harga):,}</span></div>
<div><span class="data-label">VOLATILITY</span><span class="data-value" style="color: {'#EF4444' if volatility_badge == 'HIGH' else '#10B981'};">{volatility_badge}</span></div>
<div><span class="data-label">MA20 (EMA)</span><span class="data-value">{int(ma20):,}</span></div>
</div>
<div style="margin-top:10px; display:flex; gap:4px; flex-wrap:wrap;">
<span class="{cond_price}">• PRICE>MA20</span>
<span class="{cond_ma}">• MA20>MA50</span>
</div>
</div>
"""
                st.markdown(html_col3, unsafe_allow_html=True)
                
            with col4:
                html_col4 = f"""
<div class="pro-card" style="height:100%; text-align:center;">
<div class="card-label" style="justify-content:center; border:none; margin-bottom:0;">🎯 ENTRY AREA</div>
<div style="font-size:22px; font-weight:800; color:#FAFAFA; margin:2px 0;">{int(s.get('AREA BELI', 0)):,}</div>
<div style="color:#71717A; font-size:9px;">Toleransi (MA20)</div>
</div>
"""
                st.markdown(html_col4, unsafe_allow_html=True)
                
            col5, col6 = st.columns([1.5, 1])
            with col5:
                html_col5 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">🛡️ KEPUTUSAN STRATEGI</div>
<div style="background: {action_bg}; border: 1px solid {action_color}; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 8px;">
<div style="color: {action_color}; font-size: 16px; font-weight: 800;">{action_text}</div>
</div>
<div style="color:#A1A1AA; font-size:10px;">Status: <b style="color:#C6A87C;">{grade}</b></div>
</div>
"""
                st.markdown(html_col5, unsafe_allow_html=True)
                
            with col6:
                html_col6 = f"""
<div class="pro-card" style="height:100%; text-align:center;">
<div class="card-label" style="justify-content:center; border:none; margin-bottom:0;">🚨 STOP LOSS</div>
<div style="font-size:22px; font-weight:800; color:#EF4444; margin:2px 0;">{int(s.get('TRAILING STOP', 0)):,}</div>
<div style="color:#71717A; font-size:9px;">Auto Chandelier</div>
</div>
"""
                st.markdown(html_col6, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: CLUSTERING OTOMATIS
    # ------------------------------------------
    with tab_cluster:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>🎯 Kategori Pilihan Engine</h4>", unsafe_allow_html=True)
        
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        
        # 1. Cluster Serok Bawah
        df_serok = df_all[~df_all['SEROK_SIGNAL'].str.contains("TDK ADA")]
        st.markdown("<div class='sop-title'>🟢 CLUSTER: Sinyal Serok Bawah (Rebound/Divergence)</div>", unsafe_allow_html=True)
        if not df_serok.empty:
            st.dataframe(df_serok[['TICKER', 'HARGA', 'SEROK_SIGNAL', 'STATUS_BANDAR']], hide_index=True, use_container_width=True)
        else:
            st.markdown("<div style='color:#71717A; font-size:12px; margin-bottom:15px;'>Belum ada saham yang masuk kriteria Serok Bawah saat ini.</div>", unsafe_allow_html=True)
            
        # 2. Cluster Dividend Investing (Menggunakan YIELD_RAW yang sudah ternormalisasi > 2%)
        if 'YIELD_RAW' in df_all.columns:
            df_div = df_all[df_all['YIELD_RAW'] >= 2.0].sort_values(by='YIELD_RAW', ascending=False)
            st.markdown("<div class='sop-title' style='margin-top:20px;'>💰 CLUSTER: Dividend Investing (Yield >= 2%)</div>", unsafe_allow_html=True)
            if not df_div.empty:
                st.dataframe(df_div[['TICKER', 'HARGA', 'YIELD', 'ROE', 'PER']], hide_index=True, use_container_width=True)
            else:
                st.markdown("<div style='color:#71717A; font-size:12px; margin-bottom:15px;'>Tidak ada saham dividen tinggi di database scan saat ini.</div>", unsafe_allow_html=True)
                
        # 3. Cluster Bandar Akumulasi Kuat
        df_bandar = df_all[df_all['STATUS_BANDAR'].str.contains("AKUMULASI") | df_all['STATUS_BANDAR'].str.contains("MARK-UP")]
        st.markdown("<div class='sop-title' style='margin-top:20px;'>🐋 CLUSTER: Smart Money Flow (Akumulasi Bandar)</div>", unsafe_allow_html=True)
        if not df_bandar.empty:
            st.dataframe(df_bandar[['TICKER', 'HARGA', 'STATUS_BANDAR', 'WPI_SCORE']], hide_index=True, use_container_width=True)
        else:
            st.markdown("<div style='color:#71717A; font-size:12px; margin-bottom:15px;'>Belum terdeteksi akumulasi masif saat ini.</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 3: SOP & PANDUAN PENGGUNAAN
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
            </ol>
        </div>
        
        <div class="sop-box">
            <div class="sop-title">Penjabaran Hasil Data Reel</div>
            <ul style="margin-left: -15px; margin-bottom:0;">
                <li style="margin-bottom:8px;"><b>Teknikal (Kondisi Harga):</b> Menggunakan Moving Average (MA20 & MA50). Jika <i>Price > MA20</i> berarti saham sedang dalam trend naik jangka pendek. Area Beli ideal selalu di dekat MA20. Volatilitas diukur dengan indikator ATR (Average True Range).</li>
                <li style="margin-bottom:8px;"><b>WPI (Whale Pressure Index):</b> Indikator skor dari 0-100 yang mengukur seberapa kuat tekanan pembeli memenangkan harga di hari itu. Skor di atas 70 menunjukkan dominasi <i>buyer/bandar</i> yang kuat dari level terendah hari itu.</li>
                <li style="margin-bottom:8px;"><b>Bandarmologi (Smart Money):</b> Algoritma ini menganalisa anomali Volume yang melonjak (Volume Spike) lalu mengawinkannya dengan bentuk <i>Candlestick shadow</i>. 
                Jika volume tinggi di dasar jurang, status menjadi <b>Akumulasi Dasar</b>. Jika volume meledak di pucuk atas, awas <b>Distribusi Pucuk</b>.</li>
                <li style="margin-bottom:8px;"><b>Fundamental (ROE & YIELD):</b> <b>ROE</b> menunjukkan seberapa efisien perusahaan mencetak laba bersih dari modalnya (>10% bagus). <b>YIELD</b> menunjukkan persentase keuntungan dari Dividen yang dibagikan rutin (Cocok untuk investasi pasif).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
