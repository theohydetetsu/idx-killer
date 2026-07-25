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
import streamlit.components.v1 as components

warnings.filterwarnings('ignore')

# ==========================================
# 0. REACTIVE ENGINE & PERSISTENT CACHE (V18.0)
# ==========================================
CACHE_FILE = "jihan_ghina_saham_cache_v180.json"

def load_reactive_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                loaded_stocks = cache_data.get("raw_stocks", [])
                ihsg_data = cache_data.get("ihsg", {})
                if loaded_stocks and isinstance(loaded_stocks, list):
                    return loaded_stocks, cache_data.get("last_update", None), ihsg_data
        except: pass
    return [], None, {}

if "raw_stocks" not in st.session_state:
    st.session_state.raw_stocks, st.session_state.last_update, st.session_state.ihsg_data = load_reactive_cache()

if "reactive_mode" not in st.session_state: st.session_state.reactive_mode = False

# ==========================================
# 1. LUXURY UI & EXTREME MOBILE CSS
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate v18.0", page_icon="✨", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #050505 !important; color: #A1A1AA !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; max-width: 100% !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    section[data-testid="stSidebar"] { background-color: #09090B !important; border-right: 1px solid #1F1F22 !important; min-width: 220px !important; max-width: 220px !important; }
    section[data-testid="stSidebar"] * { color: #A1A1AA !important; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #09090B !important; border: 1px solid #27272A !important; border-radius: 8px !important; }
    div[data-baseweb="select"] span, input { color: #FAFAFA !important; font-weight: 600 !important; font-size: 13px !important; }
    
    .pro-card { background: linear-gradient(145deg, #121214, #09090B); border: 1px solid #27272A; border-radius: 10px; padding: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 10px; }
    .card-label { color: #C6A87C; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 6px;}
    .header-profile { display: flex; justify-content: space-between; align-items: center; }
    .logo-circle { width: 40px; height: 40px; border-radius: 10px; background: linear-gradient(135deg, #C6A87C 0%, #8E793E 100%); display: flex; justify-content: center; align-items: center; font-size: 16px; font-weight: 800; color: #050505; margin-right: 12px;}
    .ticker-title { font-size: 22px; font-weight: 800; color: #FAFAFA; line-height: 1.1; display:flex; align-items:center; gap: 6px;}
    .badge-primary { background: rgba(198, 168, 124, 0.1); color: #C6A87C; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; border: 1px solid rgba(198, 168, 124, 0.3);}
    .badge-green { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);}
    .badge-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3);}
    .data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;}
    .data-label { font-size: 9px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; display:block;}
    .data-value { font-size: 13px; color: #FAFAFA; font-weight: 700; display:block;}
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 5px;}
    .stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 600; background: transparent; padding: 8px 10px; border: none; font-size:12px;}
    .stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
    
    .sop-title { color: #C6A87C; font-size: 16px; font-weight: 700; margin-bottom: 5px; margin-top: 15px;}
    .sop-text { color: #A1A1AA; font-size: 13px; line-height: 1.6;}
    .sop-highlight { color: #FAFAFA; font-weight: 600;}
    
    @media (max-width: 768px) {
        .data-grid { grid-template-columns: 1fr 1fr !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE DATA FETCHING
# ==========================================
MASTER_UNIVERSE = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT", "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM", "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR", "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR", "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS", "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP", "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE", "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH", "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA", "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS", "BBYB", "AGRO", "ARKA"]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M:%S")

def hitung_rsi(df, periods=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/periods, min_periods=periods).mean()
    loss = (-1 * delta.clip(upper=0)).ewm(alpha=1/periods, min_periods=periods).mean()
    return 100 - (100 / (1 + (gain / loss)))

def fetch_ihsg_compass():
    try:
        df = yf.download("^JKSE", period="5d", progress=False)
        if df.empty: return {"harga": 0, "change": 0, "trend": "NEUTRAL"}
        close_now = float(df['Close'].iloc[-1])
        close_prev = float(df['Close'].iloc[-2])
        change = ((close_now - close_prev) / close_prev) * 100
        trend = "BULLISH" if change > 0 else "BEARISH"
        return {"harga": close_now, "change": change, "trend": trend}
    except: return {"harga": 0, "change": 0, "trend": "NEUTRAL"}

def fetch_single_stock(emiten):
    try:
        df = yf.download(emiten, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
        df = df.ffill().dropna(subset=['Close'])
        
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        # Hitung ATR & Volatilitas untuk StopLoss & TP
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        df['ATR'] = np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1).rolling(14).mean()
        df['Chandelier_Exit'] = df['High'].rolling(22).max() - (df['ATR'] * 3.0)
        df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
        
        harga_skg = float(df['Close'].iloc[-1])
        open_skg = float(df['Open'].iloc[-1])
        high_skg = float(df['High'].iloc[-1])
        low_skg = float(df['Low'].iloc[-1])
        vol_skg = float(df['Volume'].iloc[-1])
        ema20_skg = float(df['EMA20'].iloc[-1])
        sma50_skg = float(df['SMA50'].iloc[-1])
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        atr_skg = float(df['ATR'].iloc[-1])
        
        is_bullish = harga_skg >= open_skg
        body_size = abs(open_skg - harga_skg)
        lower_shadow = (open_skg if is_bullish else harga_skg) - low_skg
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        
        low_20 = float(df['Low'].tail(20).min())
        is_near_bottom = (harga_skg - low_20) / low_20 <= 0.06
        is_vol_spike = vol_skg > (vol_sma20 * 1.2)
        
        serok_signal = "🐋 WHALE ABSORPTION" if (is_vol_spike and lower_shadow > body_size * 1.5 and is_near_bottom) else "➖ TDK ADA"
        
        if is_vol_spike:
            if lower_shadow > (body_size * 1.5): status_bandar = "🐋 AKUMULASI DASAR"
            elif upper_shadow > (body_size * 1.5): status_bandar = "🩸 DISTRIBUSI PUCUK"
            elif is_bullish and wpi_score > 70: status_bandar = "🚀 MARK-UP BERINGAS"
            elif is_bullish: status_bandar = "🟢 AKUMULASI AWAL"
            else: status_bandar = "💥 MARK-DOWN"
        else: status_bandar = "➖ NEUTRAL"
            
        setup_score = sum([harga_skg > ema20_skg, wpi_score > 85, vol_skg > vol_sma20*2])
        if setup_score >= 2 and wpi_score >= 70: setup_grade = "⭐ SETUP A+"
        elif setup_score >= 1: setup_grade = "✔️ SETUP B"
        else: setup_grade = "⚠️ WAIT/WATCHLIST"
        
        # TARGET PROFIT ENGINE (RR 1:1.5 dan 1:2)
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg: trailing_stop = harga_skg - (atr_skg * 2)
        
        risk_per_share = harga_skg - trailing_stop
        tp1 = harga_skg + (risk_per_share * 1.5)
        tp2 = harga_skg + (risk_per_share * 2.5)

        tkr = yf.Ticker(emiten)
        info = tkr.info if tkr.info else {}
        
        raw_yield = info.get('dividendYield', 0)
        div_yield = 0.0 if raw_yield is None else (round(raw_yield, 2) if raw_yield > 1.0 else round(raw_yield * 100, 2))

        return {
            "TICKER": emiten.replace(".JK", ""), "HARGA": harga_skg, "MA20": ema20_skg, "MA50": sma50_skg, 
            "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3), 
            "TRAILING STOP": trailing_stop, "TP1": tp1, "TP2": tp2, "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal, "STATUS_BANDAR": status_bandar, "SETUP_GRADE": setup_grade, 
            "PER": round(info.get('trailingPE', 0.0), 2), "ROE": round(info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0, 2),
            "YIELD": f"{div_yield}%", "YIELD_RAW": div_yield, "VOLUME": vol_skg, "VOL_SMA20": vol_sma20, 
            "ATR_PCT": (atr_skg / harga_skg) * 100
        }
    except: return None

# ==========================================
# 3. SIDEBAR (MONEY MANAGEMENT ENGINE)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#C6A87C; font-size:18px; font-weight:800; margin-bottom:0;'>✨ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#71717A; font-size:9px; letter-spacing:1px; margin-bottom:20px;'>EDITION V18.0 - AUTO CUAN</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:10px; color:#A1A1AA; font-weight:bold; margin-bottom:5px;'>🛡️ MONEY MANAGEMENT</div>", unsafe_allow_html=True)
    modal_trading = st.number_input("Modal Trading (Rp)", min_value=100000, value=10000000, step=1000000, format="%d")
    risiko_persen = st.number_input("Risiko per Trade (%)", min_value=0.5, value=2.0, step=0.5, format="%.1f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 SCAN MARKET", use_container_width=True):
        st.session_state.raw_stocks = []
        
        my_bar = st.progress(0, text="Mengkalibrasi IHSG...")
        st.session_state.ihsg_data = fetch_ihsg_compass()
        
        # Scan Top 30 Liquid Stocks for speed in testing
        scan_list = master_tickers[:40] 
        for i, t in enumerate(scan_list):
            my_bar.progress((i + 1) / len(scan_list), text=f"Scanning {t}...")
            data = fetch_single_stock(t)
            if data: st.session_state.raw_stocks.append(data)
            gc.collect() 
        my_bar.empty()
        st.session_state.last_update = get_waktu_wib()
        
        try:
            with open(CACHE_FILE, "w") as f: 
                json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update, "ihsg": st.session_state.ihsg_data}, f)
        except: pass
        st.rerun()

# ==========================================
# 4. LIVE IHSG COMPASS & CLOCK (JS INJECTION)
# ==========================================
ihsg = st.session_state.ihsg_data if hasattr(st.session_state, 'ihsg_data') else {"harga": 0, "change": 0, "trend": "NEUTRAL"}
ihsg_color = "#10B981" if ihsg.get("change", 0) > 0 else "#EF4444"
ihsg_sign = "+" if ihsg.get("change", 0) > 0 else ""

html_live_ticker = f"""
<div style="background: linear-gradient(90deg, #09090B 0%, #121214 100%); border: 1px solid #27272A; border-radius: 8px; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 11px; color: #71717A; font-weight: 700; letter-spacing: 1px;">MARKET COMPASS</div>
        <div style="font-family: monospace; font-size: 20px; font-weight: 800; color: #FAFAFA;">IHSG : <span style="color: {ihsg_color};">{ihsg.get('harga', 0):,.2f}</span></div>
        <div style="background: rgba({ '16,185,129' if ihsg.get('change',0) > 0 else '239,68,68' }, 0.2); color: {ihsg_color}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; font-family: monospace;">{ihsg_sign}{ihsg.get('change', 0):.2f}%</div>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 8px; height: 8px; background-color: #EF4444; border-radius: 50%; box-shadow: 0 0 8px #EF4444; animation: blink 1s infinite;"></div>
        <div id="live-clock" style="font-family: monospace; font-size: 18px; color: #C6A87C; font-weight: bold; letter-spacing: 2px;"></div>
    </div>
</div>
<style>
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
</style>
<script>
    setInterval(function() {{
        var d = new Date();
        document.getElementById('live-clock').innerHTML = d.toLocaleTimeString('id-ID', {{ hour12: false }}) + " WIB";
    }}, 1000);
</script>
"""
components.html(html_live_ticker, height=75)

# ==========================================
# 5. MAIN DASHBOARD WITH SOP TAB
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN MARKET' di sidebar untuk memulai.")
else:
    tab_dash, tab_cluster, tab_sop = st.tabs(["✨ LIVE DASHBOARD", "🎯 AUTO CLUSTERING", "📖 BUKU PANDUAN & SOP"])
    
    with tab_dash:
        pilihan_ticker = st.selectbox("🔍 PENCARIAN EMITEN:", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0)
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            harga, entry, stop_loss = s.get('HARGA', 0), s.get('AREA BELI', 0), s.get('TRAILING STOP', 0)
            tp1, tp2 = s.get('TP1', 0), s.get('TP2', 0)
            
            # MONEY MANAGEMENT CALCULATION
            risiko_rp = modal_trading * (risiko_persen / 100)
            risk_per_share = entry - stop_loss
            if risk_per_share > 0:
                max_lembar = risiko_rp / risk_per_share
                max_lot = int(max_lembar / 100)
            else:
                max_lot = 0
                
            # UI Render
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"""
                <div class="pro-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div class="ticker-title" style="font-size:32px;">{s.get('TICKER')}</div>
                            <div style="color:#10B981; font-size:18px; font-weight:bold;">Rp {int(harga):,}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#71717A; font-size:10px; text-transform:uppercase; font-weight:bold;">Bandar Status</div>
                            <div style="color: #C6A87C; font-size:16px; font-weight:bold;">{s.get('STATUS_BANDAR')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    st.markdown(f"<div class='pro-card' style='text-align:center;'><div class='card-label' style='justify-content:center;'>🎯 ENTRY IDEAL</div><div style='font-size:20px; font-weight:800; color:#FAFAFA;'>Rp {int(entry):,}</div></div>", unsafe_allow_html=True)
                with col_d:
                    st.markdown(f"<div class='pro-card' style='text-align:center;'><div class='card-label' style='justify-content:center; color:#EF4444;'>🚨 STOP LOSS</div><div style='font-size:20px; font-weight:800; color:#EF4444;'>Rp {int(stop_loss):,}</div></div>", unsafe_allow_html=True)
                with col_e:
                    st.markdown(f"<div class='pro-card' style='text-align:center;'><div class='card-label' style='justify-content:center; color:#10B981;'>🚀 TP 1 (RR 1:1.5)</div><div style='font-size:20px; font-weight:800; color:#10B981;'>Rp {int(tp1):,}</div></div>", unsafe_allow_html=True)
                    
            with col_b:
                st.markdown(f"""
                <div class="pro-card" style="border-color: #C6A87C; background: rgba(198, 168, 124, 0.05); height: 100%;">
                    <div class="card-label" style="border-bottom-color: rgba(198, 168, 124, 0.3);">🛡️ MAX LOT SIZE (REKOMENDASI)</div>
                    <div style="text-align:center; padding: 15px 0;">
                        <div style="font-size:12px; color:#A1A1AA;">Berdasarkan risiko {risiko_persen}% dari modal Rp{modal_trading/1000000:.0f} Jt</div>
                        <div style="font-size:42px; font-weight:900; color:#C6A87C; margin: 10px 0; line-height:1;">{max_lot} <span style="font-size:16px;">LOT</span></div>
                        <div style="font-size:10px; color:#EF4444; font-weight:bold;">Maksimal loss dibatasi: Rp {int(risiko_rp):,}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_cluster:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px;'>🎯 Kategori Pilihan Engine</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        
        df_setup = df_all[df_all['SETUP_GRADE'].str.contains("A\+") | df_all['SETUP_GRADE'].str.contains("JACKPOT")]
        if not df_setup.empty:
            st.markdown("<div class='card-label'>🔥 TOP SETUP HARI INI</div>", unsafe_allow_html=True)
            st.dataframe(df_setup[['TICKER', 'HARGA', 'AREA BELI', 'TP1', 'STATUS_BANDAR']], hide_index=True, use_container_width=True)

    with tab_sop:
        st.markdown("""
        <div class="pro-card" style="padding: 20px;">
            <div style="border-bottom: 1px solid #27272A; padding-bottom: 10px; margin-bottom: 20px;">
                <h2 style="color: #C6A87C; margin: 0;">📖 BUKU PANDUAN & SOP J-G ULTIMATE V18.0</h2>
                <p style="color: #71717A; font-size: 12px; margin-top: 5px;">Panduan operasional resmi untuk membaca algoritma dan mengambil keputusan eksekusi trading.</p>
            </div>
            
            <div class="sop-title">1. WPI (Whale Pressure Index) Score</div>
            <div class="sop-text">
                WPI adalah indikator untuk mengukur seberapa kuat tekanan pembeli (buyer) dibandingkan penjual (seller) dalam satu hari perdagangan.<br>
                <span class="sop-highlight">▪️ Parameter / Rumus Asal:</span> Dihitung dari posisi Harga Penutupan (Close) relatif terhadap rentang pergerakan harga hari itu (High - Low).<br>
                <code>((Close - Low) / (High - Low)) * 100</code><br><br>
                <span class="sop-highlight">▪️ Cara Membaca & Kode Warna:</span><br>
                🟢 <b>> 85 (Sangat Bagus):</b> Harga ditutup hampir di pucuk tertinggi hari itu. Artinya, bandar memborong barang sampai penutupan.<br>
                🟡 <b>50 - 84 (Netral/Bagus):</b> Harga ditutup di area tengah/atas. Masih ada perlawanan seimbang.<br>
                🔴 <b>< 50 (Waspada):</b> Harga ditutup di dekat area harga terendah. Tekanan jual kuat (dibanting seller).
            </div>
            <br>
            
            <div class="sop-title">2. Smart Money (Serok Signal)</div>
            <div class="sop-text">
                Engine ini mendeteksi anomali saat market sedang panik/turun tajam, namun ada "Uang Pintar" yang menampung barang.<br>
                <span class="sop-highlight">▪️ Parameter Asal:</span> Sinyal "🐋 WHALE ABSORPTION" muncul JIKA 3 syarat ini terpenuhi bersamaan:<br>
                1. <b>Harga di Dasar:</b> Harga berada maksimal 6% dari harga terendah dalam 20 hari terakhir.<br>
                2. <b>Volume Meledak:</b> Volume transaksi melonjak >120% dari rata-rata 20 hari (SMA20 Volume).<br>
                3. <b>Candlestick Rejection:</b> Panjang ekor bawah (Lower Shadow) > 1.5 kali panjang badan (Body) candle.<br><br>
                <span class="sop-highlight">▪️ Penjelasan Hasil:</span> Ini adalah area spekulasi <i>Buy on Weakness</i> dengan probabilitas pantulan tinggi. Jika "➖ TDK ADA", pergerakan normal tanpa campur tangan bandar agresif di dasar.
            </div>
            <br>
            
            <div class="sop-title">3. Bandar Flow (Status Bandar)</div>
            <div class="sop-text">
                Menggunakan metode Price & Volume Action (VPA) sebagai proksi pergerakan Bandar (karena data broker summary tidak tersedia di Yahoo Finance).<br>
                <span class="sop-highlight">▪️ Parameter & Cara Membaca:</span><br>
                • <b>🐋 AKUMULASI DASAR:</b> Volume meledak + Ekor bawah panjang (Bandar serok di bawah).<br>
                • <b>🟢 AKUMULASI AWAL:</b> Volume meledak + Harga naik normal.<br>
                • <b>🚀 MARK-UP BERINGAS:</b> Volume meledak + Harga naik + WPI > 70 (Bandar kerek harga naik agresif).<br>
                • <b>🩸 DISTRIBUSI PUCUK:</b> Volume meledak + Ekor atas panjang (Bandar jualan saat ritel FOMO).<br>
                • <b>💥 MARK-DOWN:</b> Volume meledak + Harga ditutup merah pekat (Bandar buang barang).<br>
                • <b>➖ NEUTRAL:</b> Volume transaksi biasa saja / di bawah rata-rata.
            </div>
            <br>
            
            <div class="sop-title">4. Analisis Bid & Offer (Data Limitations & Analogi Logika)</div>
            <div class="sop-text">
                <span class="sop-highlight">▪️ Apakah Bid & Offer ada di sistem ini?</span> Belum ada.<br>
                Data Bid & Offer adalah data Level 2 (tertutup) yang tidak disediakan oleh API Yahoo Finance. Data ini hanya bisa diakses via API berbayar dari Bursa Efek Indonesia (IDX) atau sekuritas.<br><br>
                <span class="sop-highlight">▪️ Analogi Logika (Cara Script Ini Mengakali):</span><br>
                Karena tidak ada Bid/Offer, script menggunakan <b>Volume Spike & Shadow Analysis</b> (seperti poin 3). Analogi logikanya: Kita tidak perlu tertipu melihat antrean Bid/Offer yang sering kali dipalsukan (Fake Bid/Offer) oleh bandar. Kita cukup melihat <b>Hasil Akhirnya (Volume transaksi valid & Harga Penutupan)</b>. Jika <i>Bid</i> dicabut dan harga dibanting, itu akan otomatis terbaca di script sebagai "💥 MARK-DOWN" atau membentuk ekor atas yang panjang.
            </div>
        </div>
        """, unsafe_allow_html=True)
