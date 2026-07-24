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
# 0. REACTIVE ENGINE & PERSISTENT CACHE (V17.4)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v174.json"

def load_reactive_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                loaded_stocks = cache_data.get("raw_stocks", [])
                if loaded_stocks and isinstance(loaded_stocks, list):
                    if len(loaded_stocks) > 0 and "ATR_PCT" not in loaded_stocks[0]:
                        return [], None
                return loaded_stocks, cache_data.get("last_update", None)
        except: pass
    return [], None

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update = load_reactive_cache()

if "reactive_mode" not in st.session_state:
    st.session_state.reactive_mode = False

if "current_tf" not in st.session_state: 
    st.session_state.current_tf = "1 Hari (Daily)"

# ==========================================
# 1. LUXURY UI & MOBILE CSS CONFIGURATION
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v17.4", page_icon="✨", layout="wide")

# CSS diatur ulang untuk tema Luxury (Hitam/Emas) & Presisi Layar HP
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Background Onyx Black */
    [data-testid="stAppViewContainer"] { background-color: #050505 !important; color: #A1A1AA !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* Mobile precision padding */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 100% !important; }
    
    /* Narrow Sidebar Luxury */
    section[data-testid="stSidebar"] { 
        background-color: #09090B !important; 
        border-right: 1px solid #1F1F22 !important; 
        min-width: 240px !important; 
        max-width: 240px !important;
    }
    section[data-testid="stSidebar"] * { color: #A1A1AA !important; }
    
    /* Elegant Cards */
    .pro-card { 
        background: linear-gradient(145deg, #121214, #09090B);
        border: 1px solid #27272A; 
        border-radius: 12px; 
        padding: 16px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        margin-bottom: 12px;
    }
    
    /* Gold Accents */
    .card-label { color: #C6A87C; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 6px;}
    
    .header-profile { display: flex; justify-content: space-between; align-items: center; }
    .logo-circle { width: 50px; height: 50px; border-radius: 12px; background: linear-gradient(135deg, #C6A87C 0%, #8E793E 100%); display: flex; justify-content: center; align-items: center; font-size: 20px; font-weight: 800; color: #050505; margin-right: 15px;}
    .ticker-title { font-size: 28px; font-weight: 800; color: #FAFAFA; line-height: 1.1; display:flex; align-items:center; gap: 8px;}
    .ticker-desc { color: #A1A1AA; font-size: 12px; font-weight: 500; margin-top: 4px; }
    
    /* Refined Badges */
    .badge-primary { background: rgba(198, 168, 124, 0.1); color: #C6A87C; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(198, 168, 124, 0.3);}
    .badge-green { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
    .badge-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
    
    .score-box { background: #050505; border: 1px solid #27272A; border-radius: 8px; padding: 10px 15px; text-align: center; }
    .score-value { font-size: 24px; font-weight: 800; color: #C6A87C; line-height: 1; margin: 4px 0;}
    
    .warning-banner { background-color: rgba(198, 168, 124, 0.05); border: 1px solid rgba(198, 168, 124, 0.2); border-radius: 8px; padding: 12px; margin-top: 10px; margin-bottom: 15px; color: #C6A87C; font-size: 11px; font-weight: 500; display: flex; align-items: center; gap: 8px;}
    
    .data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;}
    .data-point span { display: block; }
    .data-label { font-size: 10px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px;}
    .data-value { font-size: 15px; color: #FAFAFA; font-weight: 700;}
    
    .meter-container { background: #27272A; height: 6px; border-radius: 3px; margin-top: 20px; position: relative;}
    .meter-fill { background: linear-gradient(90deg, #EF4444 0%, #C6A87C 50%, #10B981 100%); height: 100%; border-radius: 3px;}
    .meter-labels { display: flex; justify-content: space-between; font-size: 10px; color: #71717A; font-weight: 600; margin-top: 6px;}
    
    /* Tabs Overhaul */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 15px;}
    .stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 600; background: transparent; padding: 8px 0; border: none; font-size:13px;}
    .stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
    
    /* HP/Mobile Specific Overrides */
    @media (max-width: 768px) {
        .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
        .header-profile { flex-direction: column; text-align: center; gap: 10px; }
        .logo-circle { margin: 0 auto; width: 45px; height: 45px; font-size: 16px; }
        .ticker-title { justify-content: center; flex-wrap: wrap; font-size: 24px;}
        .data-grid { grid-template-columns: 1fr 1fr !important; gap: 10px;}
        .score-box { width: 100%; }
        .pro-card { padding: 14px; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE DATA FETCHING & INDICATORS
# ==========================================
MASTER_UNIVERSE = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT", "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM", "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR", "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR", "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS", "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP", "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE", "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH", "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA", "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS", "BBYB", "AGRO", "ARKA", "BABP", "BACA", "BGTG", "BHIT", "BIPI", "BKDP", "BVIC", "CARE", "CARS", "CASS", "CBEZ", "CEKA", "CENT", "CFIN", "CINT", "CMNP", "COAL", "DANG", "DART", "DILD", "DKFT", "DMAS", "DSSA", "EAST", "ELSA", "EMDE", "EPMT", "FAST", "FPNI", "FREN", "GJTL", "GLOB", "GZCO", "HOKI", "HOME", "IATA", "IBST", "IGAR", "IMAS", "INPC", "IPCC", "IPCM", "IPTV", "IRRA", "JAWA", "JECC", "JPFA", "KBLI", "KBLV", "KIJA", "KINO", "KPIG", "KRAS", "LINK", "LPCK", "LPKR", "LPPF", "MAIN", "MALA", "MARI", "MBSS", "MCOL", "MDLN", "MGRO", "MICE", "MLBI", "MLIA", "MLPL", "MLPT", "MPMX", "MTDL", "MTLA", "NELY", "NRCA", "OBMD", "OASA", "OMRE", "PANS", "PBRX", "PGLI", "PNBN", "PNBS", "PNIN", "PNLF", "POLU", "PRDA", "PSAB", "PTRO", "PURA", "RALS", "RANC", "RBMS", "RDTX", "RELI", "RICY", "RIGS", "RIMO", "ROTI", "SAMA", "SAME", "SCNP", "SDRA", "SIMP", "SMCB", "SMMT", "SMPL", "SMSM", "SOCI", "SPMA", "SRAI", "SRIL", "SSSC", "STTP", "SUDI", "SUGI", "SULI", "TARA", "TAXI", "TCID", "TEBE", "TGKA", "TINS", "TIRA", "TOTO", "TRIS", "TRST", "TSPC", "TUGU", "ULTJ", "UNIC", "UNIT", "VINS", "VIVA", "VOKS", "WEGE", "WIM", "WOMF", "WSBP", "WSKT", "WTON", "YPAS", "ZBRA"]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M WIB")

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
        if df_market.empty: return master_tickers[:300] 
        top_gainers = df_market.nlargest(120, 'Change')['Ticker'].tolist()
        top_liquid = df_market.nlargest(100, 'TransVal')['Ticker'].tolist()
        top_volatile = df_market.nlargest(80, 'VolatilityScore')['Ticker'].tolist()
        return list(set(top_gainers + top_liquid + top_volatile))[:300]
    except: return master_tickers[:300] 

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
        
        harga_skg, open_skg, high_skg, low_skg, vol_skg, prev_close = float(df['Close'].iloc[-1]), float(df['Open'].iloc[-1]), float(df['High'].iloc[-1]), float(df['Low'].iloc[-1]), float(df['Volume'].iloc[-1]), float(df['Close'].iloc[-2])
        ema20_skg, sma50_skg = float(df['EMA20'].iloc[-1]), float(df['SMA50'].iloc[-1])
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        
        low_20 = float(df['Low'].tail(20).min())
        is_near_bottom = (harga_skg - low_20) / low_20 <= 0.06
        has_bullish_div = check_bullish_divergence(df, window=20)
        
        is_bullish = harga_skg >= open_skg
        body_size, lower_shadow = abs(open_skg - harga_skg), (open_skg if is_bullish else harga_skg) - low_skg
        is_whale_absorption = (vol_skg > vol_sma20 * 1.3) and (lower_shadow > body_size * 1.5) and is_near_bottom

        if has_bullish_div and is_near_bottom: serok_signal = "🎯 BULLISH DIVERGENCE"
        elif is_whale_absorption: serok_signal = "🐋 WHALE ABSORPTION"
        elif (float(df['Stoch_K'].iloc[-1]) < 30) and (float(df['Stoch_K'].iloc[-1]) > float(df['Stoch_D'].iloc[-1])) and is_near_bottom: serok_signal = "🟢 OVERSOLD REBOUND"
        else: serok_signal = "➖ TDK ADA SEROK"

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
        return {
            "TICKER": kode, "HARGA": harga_skg, "MA20": ema20_skg, "MA50": sma50_skg, 
            "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3), 
            "TRAILING STOP": trailing_stop, "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal, "STATUS_BANDAR": status_bandar, "SETUP_GRADE": setup_grade, 
            "PER": round(info.get('trailingPE', 0.0), 2), "ROE": round(info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0, 2),
            "RET_1D": ((harga_skg - prev_close) / prev_close * 100), "VOLUME": vol_skg, "VOL_SMA20": vol_sma20, 
            "ATR_PCT": (float(df['ATR'].iloc[-1]) / harga_skg) * 100, "NAME": info.get('longName', kode)
        }
    except Exception as e: return None

# ==========================================
# 3. SIDEBAR (NARROW LUXURY)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #C6A87C; font-size: 20px; font-weight: 800; margin-bottom: 0px;'>✨ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #71717A; font-size: 10px; letter-spacing: 2px; margin-bottom: 20px;'>LUXURY EDITION V17.4</p>", unsafe_allow_html=True)
    
    tf_pilihan = st.selectbox("⏱️ Timeframe Analisis:", ("1 Hari (Daily)", "1 Minggu (Weekly)"), index=0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='color:#FAFAFA; font-size:11px; font-weight:700; margin-bottom:5px;'>⚙️ AUTO-SYNC MATRIX</div>", unsafe_allow_html=True)
    reactive_on = st.toggle("Live Engine Mode", value=st.session_state.reactive_mode)
    if reactive_on != st.session_state.reactive_mode:
        st.session_state.reactive_mode = reactive_on
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 JALANKAN ENGINE", use_container_width=True):
        st.session_state.raw_stocks = []
        radar_bar = st.progress(0, text="Mendeteksi 300 Saham...")
        dynamic_tickers = get_dynamic_market_roster()
        radar_bar.empty()
        
        my_bar = st.progress(0, text=f"Deep Scanning...")
        for i, t in enumerate(dynamic_tickers):
            my_bar.progress((i + 1) / len(dynamic_tickers), text=f"Menganalisis {t} ({i+1}/{len(dynamic_tickers)})")
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

# ==========================================
# 4. MAIN DASHBOARD (NO INDENTATION HTML)
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 JALANKAN ENGINE' di sidebar untuk memulai scanning.")
else:
    tab_dash, tab_table = st.tabs(["✨ LUXURY DASHBOARD", "🗄️ DATABASE TABEL"])
    
    with tab_dash:
        col_search, _ = st.columns([1, 2])
        with col_search:
            pilihan_ticker = st.selectbox("🔍 Cari Emiten", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0, label_visibility="collapsed")
        
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            grade = s.get("SETUP_GRADE", "WAIT")
            atr_pct = s.get('ATR_PCT', 0)
            volatility_badge = "HIGH" if atr_pct > 4 else "NORMAL"
            vol_color_class = "badge-red" if atr_pct > 4 else "badge-green"
            
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
            
            # ATURAN PENTING: HTML dibawah tidak boleh ada spasi indentasi di awal baris!
            html_header = f"""
<div class="pro-card">
<div class="header-profile">
<div style="display:flex; align-items:center;">
<div class="logo-circle">{s.get('TICKER', 'XX')[:2]}</div>
<div>
<div class="ticker-title">{s.get('TICKER', '')} <span class="badge-primary">✨ V17.4</span></div>
<div class="ticker-desc">{s.get('NAME', '')}</div>
</div>
</div>
<div class="score-box">
<div style="font-size:9px; color:#71717A; letter-spacing:1px; text-transform:uppercase;">WPI Score</div>
<div class="score-value">{s.get('WPI_SCORE', 0):.2f}</div>
<div style="font-size:9px; color:#C6A87C;">Tekanan Volume</div>
</div>
</div>
</div>

<div class="warning-banner">
<span style="font-size:14px;">✨</span> 
LUXURY ENGINE ACTIVE. Data tersimpan aman di persistent cache.
</div>
"""
            st.markdown(html_header, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                html_col1 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">⚡ RINGKASAN STRATEGI</div>
<div style="display:flex; justify-content:space-between; border-bottom: 1px solid #27272A; padding-bottom: 12px;">
<div>
<div class="data-label">FUNDAMENTAL</div>
<div class="data-value" style="font-size:13px;">ROE <span style="color:#C6A87C;">{s.get('ROE', 0)}%</span> &nbsp;|&nbsp; PER <span style="color:#C6A87C;">{s.get('PER', 0)}x</span></div>
</div>
<div style="text-align:right;">
<div class="data-label">BANDAR FLOW</div>
<div class="data-value" style="color: {'#10B981' if 'AKUMULASI' in status_bandar else '#C6A87C' if 'NEUTRAL' in status_bandar else '#EF4444'}; font-size:13px;">{status_bandar}</div>
</div>
</div>
<div class="meter-container">
<div class="meter-fill" style="width: {s.get('WPI_SCORE', 0)}%;"></div>
</div>
<div class="meter-labels">
<span>BEARISH</span>
<span>NEUTRAL</span>
<span>BULLISH</span>
</div>
</div>
"""
                st.markdown(html_col1, unsafe_allow_html=True)
                
            with col2:
                html_col2 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">🌐 SMART MONEY</div>
<div style="text-align:center; margin: 10px 0;">
<div style="font-size:26px; font-weight:800; color:{'#10B981' if vol > vol_sma else '#A1A1AA'};">
{vol/1000000:.1f}M
</div>
<div class="badge-{'green' if vol > vol_sma else 'red'}" style="display:inline-block; margin-top:4px;">
{'VOLUME SPIKE' if vol > vol_sma else 'VOLUME DRY'}
</div>
</div>
<div style="display:flex; justify-content:space-between; font-size:11px; font-weight:600; margin-top:12px; border-top: 1px solid #27272A; padding-top:8px;">
<span style="color:#10B981;">AVG: {vol_sma/1000000:.1f}M</span>
<span style="color:#EF4444;">SIG: {serok_sig}</span>
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
<div class="data-point">
<span class="data-label">LAST PRICE</span>
<span class="data-value">{int(harga):,}</span>
</div>
<div class="data-point">
<span class="data-label">VOLATILITY</span>
<span class="data-value" style="color: {'#EF4444' if volatility_badge == 'HIGH' else '#10B981'};">{volatility_badge} <span style="font-size:10px; color:#71717A;">{atr_pct:.1f}%</span></span>
</div>
<div class="data-point">
<span class="data-label">MA20 (EMA)</span>
<span class="data-value">{int(ma20):,}</span>
</div>
</div>
<div style="margin-top:15px; display:flex; gap:6px; flex-wrap:wrap;">
<span class="{cond_price}">• PRICE > MA20</span>
<span class="{cond_ma}">• MA20 > MA50</span>
<span class="{vol_color_class}">• VOLATILITY</span>
<span class="{'badge-green' if vol > vol_sma else 'badge-red'}">• LIQUIDITY</span>
</div>
</div>
"""
                st.markdown(html_col3, unsafe_allow_html=True)
                
            with col4:
                html_col4 = f"""
<div class="pro-card" style="height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
<div class="card-label" style="justify-content:center; border:none; margin-bottom:0;">🎯 ENTRY AREA</div>
<div style="font-size:26px; font-weight:800; color:#FAFAFA; margin:5px 0;">
{int(s.get('AREA BELI', 0)):,}
</div>
<div style="color:#71717A; font-size:10px;">Area toleransi koreksi (MA20).</div>
</div>
"""
                st.markdown(html_col4, unsafe_allow_html=True)
                
            col5, col6 = st.columns([1.5, 1])
            
            with col5:
                html_col5 = f"""
<div class="pro-card" style="height:100%;">
<div class="card-label">🛡️ KEPUTUSAN STRATEGI</div>
<div style="background: {action_bg}; border: 1px solid {action_color}; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 12px;">
<div style="font-size:10px; color:#A1A1AA; text-transform:uppercase; font-weight:700; margin-bottom:4px;">RECOMMENDED ACTION</div>
<div style="color: {action_color}; font-size: 20px; font-weight: 800; letter-spacing: 1px;">{action_text}</div>
</div>
<div style="color:#A1A1AA; font-size:11px; line-height:1.4;">
Status: <b style="color:#C6A87C;">{grade}</b>. Desain presisi tanpa bug HTML.
</div>
</div>
"""
                st.markdown(html_col5, unsafe_allow_html=True)
                
            with col6:
                html_col6 = f"""
<div class="pro-card" style="height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
<div class="card-label" style="justify-content:center; border:none; margin-bottom:0;">🚨 STOP LOSS</div>
<div style="font-size:26px; font-weight:800; color:#EF4444; margin:5px 0;">
{int(s.get('TRAILING STOP', 0)):,}
</div>
<div style="color:#71717A; font-size:10px;">Trailing otomatis Chandelier.</div>
</div>
"""
                st.markdown(html_col6, unsafe_allow_html=True)

    with tab_table:
        st.markdown("<h4 style='color:#C6A87C; margin-top:10px;'>🗄️ Database Analisis</h4>", unsafe_allow_html=True)
        df_display = pd.DataFrame(st.session_state.raw_stocks)
        if not df_display.empty:
            cols_to_show = ['TICKER', 'HARGA', 'AREA BELI', 'TRAILING STOP', 'SETUP_GRADE', 'STATUS_BANDAR', 'SEROK_SIGNAL', 'WPI_SCORE']
            valid_cols = [c for c in cols_to_show if c in df_display.columns]
            st.dataframe(df_display[valid_cols], use_container_width=True, height=450)
