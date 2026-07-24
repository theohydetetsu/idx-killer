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
import io

warnings.filterwarnings('ignore')

# ==========================================
# 0. SISTEM CACHE & TRACKING (UPGRADED V17.0)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v170.json"

def load_smart_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                loaded_stocks = cache_data.get("raw_stocks", [])
                if loaded_stocks and isinstance(loaded_stocks, list):
                    if "SEROK_SIGNAL" not in loaded_stocks[0]:
                        return [], None
                return loaded_stocks, cache_data.get("last_update", None)
        except: pass
    return [], None

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update = load_smart_cache()

if "scan_clicked" not in st.session_state: st.session_state.scan_clicked = len(st.session_state.raw_stocks) > 0
if "current_tf" not in st.session_state: st.session_state.current_tf = "1 Hari (Daily)"

# ==========================================
# 1. KONFIGURASI HALAMAN & UI STOCKS.LY STYLE
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v17.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global App Background & Font */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #0B0E14 !important; color: #8B98A9 !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* Layout */
    .block-container { padding-top: 1.5rem !important; max-width: 95% !important; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #0F131C !important; border-right: 1px solid #1E2638; }
    section[data-testid="stSidebar"] * { color: #8B98A9 !important; }
    
    /* Dashboard Cards Style (Like the Image) */
    .dashboard-grid { display: flex; flex-direction: column; gap: 15px; margin-top: 15px; }
    .row-flex { display: flex; gap: 15px; }
    .col-flex { flex: 1; display: flex; flex-direction: column; gap: 15px; }
    
    .pro-card { 
        background-color: #121722; 
        border: 1px solid #1E2638; 
        border-radius: 16px; 
        padding: 24px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Card Headers */
    .card-label { color: #8B98A9; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;}
    
    /* Header Profile Card */
    .header-profile { display: flex; justify-content: space-between; align-items: center; }
    .logo-circle { width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); display: flex; justify-content: center; align-items: center; font-size: 28px; font-weight: 900; color: white; margin-right: 20px;}
    .ticker-title { font-size: 36px; font-weight: 900; color: #FFFFFF; line-height: 1.1; display:flex; align-items:center; gap: 10px;}
    .ticker-desc { color: #8B98A9; font-size: 14px; font-weight: 500; margin-top: 4px; }
    
    /* Badges */
    .badge-primary { background: rgba(59, 130, 246, 0.15); color: #3B82F6; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.3);}
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
    .badge-yellow { background: rgba(245, 158, 11, 0.15); color: #F59E0B; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; border: 1px solid rgba(245, 158, 11, 0.3);}
    
    /* Score Box */
    .score-box { background: #0B0E14; border: 1px solid #1E2638; border-radius: 12px; padding: 15px 25px; text-align: center; }
    .score-value { font-size: 32px; font-weight: 900; color: #FFFFFF; line-height: 1; margin: 5px 0;}
    
    /* Warning Banner */
    .warning-banner { background-color: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px; padding: 16px; margin-top: 15px; color: #F59E0B; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 10px;}
    
    /* Data Points */
    .data-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 20px;}
    .data-point span { display: block; }
    .data-label { font-size: 11px; color: #8B98A9; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;}
    .data-value { font-size: 18px; color: #FFFFFF; font-weight: 800;}
    
    /* Progress Bar custom */
    .meter-container { background: #1E2638; height: 8px; border-radius: 4px; margin-top: 25px; position: relative;}
    .meter-fill { background: linear-gradient(90deg, #EF4444 0%, #10B981 100%); height: 100%; border-radius: 4px;}
    .meter-labels { display: flex; justify-content: space-between; font-size: 11px; color: #8B98A9; font-weight: 600; margin-top: 8px;}
    
    /* Decision Box */
    .decision-box { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px;}
    .decision-text { color: #F59E0B; font-size: 20px; font-weight: 900; letter-spacing: 1px; margin:0;}
    
    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1E2638; gap: 20px;}
    .stTabs [data-baseweb="tab"] { color: #8B98A9; font-weight: 600; background: transparent; padding: 10px 0; border: none;}
    .stTabs [aria-selected="true"] { color: #3B82F6; border-bottom: 2px solid #3B82F6;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE DATA FETCHING & INDICATORS
# ==========================================
# (Mempertahankan logika aslimu utuh agar performa AI tetap tajam)
MASTER_UNIVERSE = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT", "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM", "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR", "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR", "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS", "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP", "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE", "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH", "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA", "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS", "BBYB", "AGRO", "ARKA", "BABP", "BACA", "BGTG", "BHIT", "BIPI", "BKDP", "BVIC", "CARE", "CARS", "CASS", "CBEZ", "CEKA", "CENT", "CFIN", "CINT", "CMNP", "COAL", "DANG", "DART", "DILD", "DKFT", "DMAS", "DSSA", "EAST", "ELSA", "EMDE", "EPMT", "FAST", "FPNI", "FREN", "GJTL", "GLOB", "GZCO", "HOKI", "HOME", "IATA", "IBST", "IGAR", "IMAS", "INPC", "IPCC", "IPCM", "IPTV", "IRRA", "JAWA", "JECC", "JPFA", "KBLI", "KBLV", "KIJA", "KINO", "KPIG", "KRAS", "LINK", "LPCK", "LPKR", "LPPF", "MAIN", "MALA", "MARI", "MBSS", "MCOL", "MDLN", "MGRO", "MICE", "MLBI", "MLIA", "MLPL", "MLPT", "MPMX", "MTDL", "MTLA", "NELY", "NRCA", "OBMD", "OASA", "OMRE", "PANS", "PBRX", "PGLI", "PNBN", "PNBS", "PNIN", "PNLF", "POLU", "PRDA", "PSAB", "PTRO", "PURA", "RALS", "RANC", "RBMS", "RDTX", "RELI", "RICY", "RIGS", "RIMO", "ROTI", "SAMA", "SAME", "SCNP", "SDRA", "SIMP", "SMCB", "SMMT", "SMPL", "SMSM", "SOCI", "SPMA", "SRAI", "SRIL", "SSSC", "STTP", "SUDI", "SUGI", "SULI", "TARA", "TAXI", "TCID", "TEBE", "TGKA", "TINS", "TIRA", "TOTO", "TRIS", "TRST", "TSPC", "TUGU", "ULTJ", "UNIC", "UNIT", "VINS", "VIVA", "VOKS", "WEGE", "WIM", "WOMF", "WSBP", "WSKT", "WTON", "YPAS", "ZBRA"]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M WIB")

@st.cache_data(ttl=300, show_spinner=False)
def fetch_ihsg_data():
    try:
        df = yf.download("^JKSE", period="1mo", interval="1d", progress=False)
        if df.empty: return None, None, None, None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
        df = df.ffill() 
        return df, float(df['Close'].iloc[-1]), float(df['Close'].iloc[-1]) - float(df['Close'].iloc[-2]), ((float(df['Close'].iloc[-1]) - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
    except: return None, None, None, None

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

        if has_bullish_div and is_near_bottom: serok_signal = "🎯 BULLISH DIVERGENCE (JACKPOT)"
        elif is_whale_absorption: serok_signal = "🐋 WHALE BOTTOM ABSORPTION"
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
# 3. SIDEBAR STOCKS.LY STYLE
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #FFFFFF; font-size: 22px; font-weight: 900; margin-bottom: 0px;'>⚡ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8B98A9; font-size: 11px; letter-spacing: 1.5px; margin-bottom: 30px;'>QUANTUM MATRIX V17.0</p>", unsafe_allow_html=True)
    
    tf_pilihan = st.selectbox("⏱️ Timeframe Analisis:", ("1 Hari (Daily)", "1 Minggu (Weekly)"), index=0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 JALANKAN SCAN ENGINE", use_container_width=True):
        st.session_state.raw_stocks = []
        radar_bar = st.progress(0, text="Mendeteksi 300 Saham Aktif...")
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
            with open(CACHE_FILE, "w") as f: json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update}, f)
        except: pass
        st.rerun()

# ==========================================
# 4. MAIN DASHBOARD RENDERER
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 JALANKAN SCAN ENGINE' di sidebar untuk memulai.")
else:
    # Pisahkan ke dalam 2 Tab: Dashboard UI (Mirip Gambar) dan Tabel Database
    tab_dash, tab_table = st.tabs(["⚡ SINGLE STOCK DASHBOARD", "🗄️ DATABASE TABEL (300 EMITEN)"])
    
    with tab_dash:
        col_search, _ = st.columns([1, 2])
        with col_search:
            pilihan_ticker = st.selectbox("🔍 Cari Emiten (Ketik kode saham)", [s['TICKER'] for s in st.session_state.raw_stocks], index=0, label_visibility="collapsed")
        
        # Ambil data spesifik dari ticker yang dipilih
        s = next((item for item in st.session_state.raw_stocks if item["TICKER"] == pilihan_ticker), None)
        
        if s:
            # Kalkulasi visual properties
            grade = s["SETUP_GRADE"]
            if "JACKPOT" in grade or "A+" in grade:
                action_text = "BUY / ACCUMULATE"
                action_color = "#10B981"
                action_bg = "rgba(16, 185, 129, 0.1)"
            elif "WAIT" in grade:
                action_text = "WAIT / WATCHLIST"
                action_color = "#F59E0B"
                action_bg = "rgba(245, 158, 11, 0.1)"
            else:
                action_text = "SPECULATIVE BUY"
                action_color = "#3B82F6"
                action_bg = "rgba(59, 130, 246, 0.1)"
                
            volatility_badge = "HIGH" if s['ATR_PCT'] > 4 else "NORMAL"
            vol_color_class = "badge-red" if s['ATR_PCT'] > 4 else "badge-green"
            
            # --- CARD 1: HEADER ---
            st.markdown(f"""
            <div class="pro-card">
                <div class="header-profile">
                    <div style="display:flex; align-items:center;">
                        <div class="logo-circle">{s['TICKER'][:2]}</div>
                        <div>
                            <div class="ticker-title">{s['TICKER']} <span class="badge-primary">⚡ V17 ANALYTICS</span></div>
                            <div class="ticker-desc">{s['NAME']}</div>
                        </div>
                    </div>
                    <div class="score-box">
                        <div style="font-size:10px; color:#8B98A9; letter-spacing:1px; text-transform:uppercase;">WPI Score (Whale)</div>
                        <div class="score-value">{s['WPI_SCORE']:.2f}</div>
                        <div style="font-size:10px; color:#10B981;">Berdasarkan tekanan volume akhir</div>
                    </div>
                </div>
            </div>
            
            <div class="warning-banner">
                <span style="font-size:16px;">⚠️</span> 
                MARKET MASIH BERJALAN. Analisis terbaik dilakukan saat bursa tutup (pukul 16:00 WIB) untuk mendapatkan data candle konfirmasi penutupan yang valid.
            </div>
            """, unsafe_allow_html=True)
            
            # --- DASHBOARD GRID ---
            st.markdown('<div class="dashboard-grid"><div class="row-flex">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                # CARD 2: RINGKASAN STRATEGI
                st.markdown(f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">⚡ RINGKASAN STRATEGI</div>
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #1E2638; padding-bottom: 15px;">
                        <div>
                            <div class="data-label">FUNDAMENTAL</div>
                            <div class="data-value" style="font-size:14px;">ROE <span style="color:#10B981;">{s['ROE']}%</span> &nbsp;|&nbsp; PER <span style="color:#10B981;">{s['PER']}x</span></div>
                        </div>
                        <div style="text-align:right;">
                            <div class="data-label">BANDAR FLOW</div>
                            <div class="data-value" style="color: {'#10B981' if 'AKUMULASI' in s['STATUS_BANDAR'] else '#F59E0B' if 'NEUTRAL' in s['STATUS_BANDAR'] else '#EF4444'};">{s['STATUS_BANDAR']}</div>
                        </div>
                    </div>
                    
                    <div class="meter-container">
                        <div class="meter-fill" style="width: {s['WPI_SCORE']}%;"></div>
                    </div>
                    <div class="meter-labels">
                        <span>EXTREME BEARISH</span>
                        <span>NEUTRAL</span>
                        <span>EXTREME BULLISH</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                # CARD 3: VOLUME & DANA ASING (Adapted to Smart Money)
                st.markdown(f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">🌐 SMART MONEY ZONE</div>
                    <div style="text-align:center; margin: 15px 0;">
                        <div style="font-size:32px; font-weight:900; color:{'#10B981' if s['VOLUME'] > s['VOL_SMA20'] else '#EF4444'};">
                            {s['VOLUME']/1000000:.1f}M
                        </div>
                        <div class="badge-{'green' if s['VOLUME'] > s['VOL_SMA20'] else 'red'}" style="display:inline-block; margin-top:5px;">
                            {'VOLUME SPIKE DETECTED' if s['VOLUME'] > s['VOL_SMA20'] else 'VOLUME DRY / SEPI'}
                        </div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:600; margin-top:15px; border-top: 1px solid #1E2638; padding-top:10px;">
                        <span style="color:#10B981;">AVG VOL: {s['VOL_SMA20']/1000000:.1f}M</span>
                        <span style="color:#EF4444;">SEROK: {s['SEROK_SIGNAL'].split()[0]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div><div class="row-flex">', unsafe_allow_html=True)
            col3, col4 = st.columns([1.5, 1])
            
            with col3:
                # CARD 4: KONDISI HARGA
                cond_price = "badge-green" if s['HARGA'] > s['MA20'] else "badge-red"
                cond_ma = "badge-green" if s['MA20'] > s['MA50'] else "badge-red"
                
                st.markdown(f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">📈 KONDISI HARGA SAAT INI</div>
                    <div class="data-grid" style="grid-template-columns: repeat(3, 1fr);">
                        <div class="data-point">
                            <span class="data-label">LAST PRICE</span>
                            <span class="data-value">{int(s['HARGA']):,}</span>
                        </div>
                        <div class="data-point">
                            <span class="data-label">VOLATILITY</span>
                            <span class="data-value" style="color: {'#EF4444' if volatility_badge == 'HIGH' else '#10B981'};">{volatility_badge} <span style="font-size:12px; color:#8B98A9;">{s['ATR_PCT']:.1f}% ATR</span></span>
                        </div>
                        <div class="data-point">
                            <span class="data-label">MA20 (EMA)</span>
                            <span class="data-value">{int(s['MA20']):,}</span>
                        </div>
                    </div>
                    
                    <div style="margin-top:25px; display:flex; gap:10px; flex-wrap:wrap;">
                        <span class="{cond_price}">• PRICE > MA20</span>
                        <span class="{cond_ma}">• MA20 > MA50</span>
                        <span class="{vol_color_class}">• VOLATILITY (ATR)</span>
                        <span class="{'badge-green' if s['VOLUME'] > s['VOL_SMA20'] else 'badge-red'}">• LIQUIDITY OK</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                # CARD 5: ENTRY AREA
                st.markdown(f"""
                <div class="pro-card" style="height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
                    <div class="card-label" style="justify-content:center;">🎯 ENTRY AREA</div>
                    <div style="font-size:28px; font-weight:900; color:#FFFFFF; margin:10px 0;">
                        {int(s['AREA BELI']):,}
                    </div>
                    <div style="color:#8B98A9; font-size:12px;">Area toleransi koreksi sehat (MA20/Support) untuk cicil masuk.</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div><div class="row-flex">', unsafe_allow_html=True)
            col5, col6 = st.columns([1.5, 1])
            
            with col5:
                # CARD 6: KEPUTUSAN STRATEGI
                st.markdown(f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">🛡️ KEPUTUSAN STRATEGI</div>
                    
                    <div style="background: {action_bg}; border: 1px solid {action_color}; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px;">
                        <div style="font-size:11px; color:#8B98A9; text-transform:uppercase; font-weight:700; margin-bottom:5px;">RECOMMENDED ACTION</div>
                        <div style="color: {action_color}; font-size: 24px; font-weight: 900; letter-spacing: 1px;">{action_text}</div>
                    </div>
                    
                    <div style="color:#8B98A9; font-size:13px; line-height:1.5;">
                        Status sistem: <b>{s['SETUP_GRADE']}</b>. Pastikan untuk selalu memantau ledakan volume di jam bursa. Jika terjadi distribusi di area pucuk, segera amankan profit.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col6:
                # CARD 7: MANAJEMEN RISIKO (TRAILING STOP)
                st.markdown(f"""
                <div class="pro-card" style="height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
                    <div class="card-label" style="justify-content:center;">🚨 MANAJEMEN RISIKO</div>
                    <div style="font-size:28px; font-weight:900; color:#EF4444; margin:10px 0;">
                        {int(s['TRAILING STOP']):,}
                    </div>
                    <div style="color:#8B98A9; font-size:12px;">Cutloss / Trailing Stop otomatis berdasarkan Algoritma Chandelier Exit (ATR).</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div></div>', unsafe_allow_html=True)

    with tab_table:
        st.markdown("<h3 style='color:#FFFFFF;'>🗄️ Database Analisis Massal</h3>", unsafe_allow_html=True)
        # Menampilkan format DataFrame asli
        df_display = pd.DataFrame(st.session_state.raw_stocks)
        if not df_display.empty:
            df_display = df_display[['TICKER', 'HARGA', 'AREA BELI', 'TRAILING STOP', 'SETUP_GRADE', 'STATUS_BANDAR', 'SEROK_SIGNAL', 'WPI_SCORE']]
            st.dataframe(df_display, use_container_width=True, height=500)
