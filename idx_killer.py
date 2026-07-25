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
# 0. REACTIVE ENGINE & PERSISTENT CACHE
# ==========================================
CACHE_FILE = "jg_saham_cache_v17_7.json"

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

# ==========================================
# 1. LUXURY UI SETUP (V17.7 PURE CLASSIC)
# ==========================================
st.set_page_config(page_title="J-G Ultimate", page_icon="✨", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #E0E0E0 !important; }
    
    /* Header Transparan: Tombol sidebar (hamburger) tetap aman disentuh di HP */
    [data-testid="stHeader"] { background-color: transparent !important; }
    section[data-testid="stSidebar"] { background-color: #0A0D12 !important; border-right: 1px solid #1F2430 !important; }
    
    /* Sleek Tabs v17.7 */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1F2430; gap: 15px; }
    .stTabs [data-baseweb="tab"] { color: #666; font-weight: 600; padding: 12px 5px; font-size: 12px; letter-spacing: 0.5px; }
    .stTabs [aria-selected="true"] { color: #D4AF37; border-bottom: 2px solid #D4AF37; }
    
    /* Block container reset for mobile */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE DATA FETCHING
# ==========================================
MASTER_UNIVERSE = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ICBP", "INDF", "AMRT", "GOTO", "PGAS", "PTBA", "ITMG", "KLBF", "ADRO", "UNVR", "BRIS", "CPIN", "ANTM", "AMMN", "BREN", "CUAN", "PANI", "BRPT", "MDKA", "MEDC", "ARTO", "SIDO", "MYOR", "INKP", "TKIM", "SMGR", "INTP", "BFIN", "AKRA", "ESSA", "EXCL", "ISAT", "TOWR", "TBIG", "MTEL", "MAPI", "MAPA", "ACES", "ERAA", "AUTO", "NISP", "BDMN", "BTPS", "BBTN", "BNGA", "BRMS", "BUMI", "ENRG", "DEWA", "DOID", "HRUM", "INCO", "PTMP", "VKTR", "GGRM", "HMSP", "WIIM", "JSMR", "WIKA", "PTPP", "ADHI", "SMRA", "BSDE", "CTRA", "PWON", "ASRI", "SSIA", "SRTG", "BMTR", "MNCN", "EMTK", "SCMA", "BUAH", "CLEO", "CMRY", "SILO", "MIKA", "HEAL", "TPIA", "MBMA", "NCKL", "PGEO", "AVIA", "ARNA", "MARK", "INAF", "KAEF", "WOOD", "TAPG", "DSNG", "LSIP", "AALI", "SSMS", "BBYB", "AGRO", "ARKA"]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M:%S")

def fetch_ihsg_compass():
    try:
        df = yf.download("^JKSE", period="5d", progress=False)
        if df.empty: return {"harga": 0, "change": 0}
        close_now = float(df['Close'].iloc[-1])
        close_prev = float(df['Close'].iloc[-2])
        change = ((close_now - close_prev) / close_prev) * 100
        return {"harga": close_now, "change": change}
    except: return {"harga": 0, "change": 0}

def fetch_single_stock(emiten):
    try:
        df = yf.download(emiten, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
        df = df.ffill().dropna(subset=['Close'])
        
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
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
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        atr_skg = float(df['ATR'].iloc[-1])
        
        is_bullish = harga_skg >= open_skg
        body_size = abs(open_skg - harga_skg)
        lower_shadow = (open_skg if is_bullish else harga_skg) - low_skg
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        
        low_20 = float(df['Low'].tail(20).min())
        is_vol_spike = vol_skg > (vol_sma20 * 1.2)
        
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
        
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg: trailing_stop = harga_skg - (atr_skg * 2)
        
        risk_per_share = harga_skg - trailing_stop
        tp1 = harga_skg + (risk_per_share * 1.5)

        return {
            "TICKER": emiten.replace(".JK", ""), "HARGA": harga_skg, "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3), 
            "TRAILING STOP": trailing_stop, "TP1": tp1, "WPI_SCORE": round(wpi_score, 1),
            "STATUS_BANDAR": status_bandar, "SETUP_GRADE": setup_grade
        }
    except: return None

# ==========================================
# 3. SIDEBAR MENU
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#D4AF37; font-weight:800; margin-bottom:0;'>✨ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:11px; margin-bottom:30px;'>VERSI 17.7 (LUXURY)</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:12px; color:#E0E0E0; font-weight:bold; margin-bottom:10px;'>🛡️ MONEY MANAGEMENT</div>", unsafe_allow_html=True)
    modal_trading = st.number_input("Modal Trading (Rp)", min_value=100000, value=10000000, step=1000000, format="%d")
    risiko_persen = st.number_input("Risiko per Trade (%)", min_value=0.5, value=2.0, step=0.5, format="%.1f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 SCAN MARKET", use_container_width=True):
        st.session_state.raw_stocks = []
        my_bar = st.progress(0, text="Mengkalibrasi IHSG...")
        st.session_state.ihsg_data = fetch_ihsg_compass()
        scan_list = master_tickers[:40] # Bisa disesuaikan jumlah emiten
        for i, t in enumerate(scan_list):
            my_bar.progress((i + 1) / len(scan_list), text=f"Scanning {t}...")
            data = fetch_single_stock(t)
            if data: st.session_state.raw_stocks.append(data)
            gc.collect() 
        my_bar.empty()
        st.session_state.last_update = get_waktu_wib()
        try:
            with open(CACHE_FILE, "w") as f: json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update, "ihsg": st.session_state.ihsg_data}, f)
        except: pass
        st.rerun()

# ==========================================
# 4. MARKET COMPASS (COMPACT & NEAT)
# ==========================================
ihsg = st.session_state.ihsg_data if hasattr(st.session_state, 'ihsg_data') else {"harga": 0, "change": 0}
ihsg_color = "#00C853" if ihsg.get("change", 0) >= 0 else "#FF3D00"
ihsg_bg = "rgba(0, 200, 83, 0.15)" if ihsg.get("change", 0) >= 0 else "rgba(255, 61, 0, 0.15)"
ihsg_sign = "+" if ihsg.get("change", 0) > 0 else ""

html_compass = f"""
<div style="background-color: #0A0D12; border: 1px solid #1F2430; border-radius: 6px; padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div style="display: flex; flex-direction: column;">
        <span style="color: #666; font-size: 10px; font-weight: 600; letter-spacing: 1px; margin-bottom: 4px;">MARKET COMPASS</span>
        <div style="display: flex; align-items: baseline; gap: 8px;">
            <span style="color: #FFF; font-size: 16px; font-weight: 800;">IHSG :</span>
            <span style="color: {ihsg_color}; font-size: 18px; font-weight: 800;">{ihsg.get('harga', 0):,.2f}</span>
            <span style="background-color: {ihsg_bg}; color: {ihsg_color}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">{ihsg_sign}{ihsg.get('change', 0):.2f}%</span>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 6px; height: 6px; background-color: #D4AF37; border-radius: 50%; box-shadow: 0 0 5px #D4AF37; animation: blink 1.5s infinite;"></div>
        <span id="live-clock" style="color: #D4AF37; font-size: 13px; font-weight: 600; font-family: monospace;"></span>
    </div>
</div>
<style>@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.2; }} 100% {{ opacity: 1; }} }}</style>
<script>
    setInterval(function() {{
        document.getElementById('live-clock').innerHTML = new Date().toLocaleTimeString('id-ID', {{ hour12: false }}) + " WIB";
    }}, 1000);
</script>
"""
components.html(html_compass, height=75)

# ==========================================
# 5. MAIN DASHBOARD (V17.7 VERTICAL LAYOUT)
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Buka menu kiri (sidebar) dan tekan '🔄 SCAN MARKET' untuk memulai.")
else:
    tab_dash, tab_cluster, tab_sop = st.tabs(["✨ LIVE DASHBOARD", "🎯 AUTO CLUSTERING", "📖 BUKU PANDUAN"])
    
    with tab_dash:
        pilihan_ticker = st.selectbox("🔍 PENCARIAN EMITEN:", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0)
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            harga, entry, sl, tp1 = s.get('HARGA', 0), s.get('AREA BELI', 0), s.get('TRAILING STOP', 0), s.get('TP1', 0)
            
            # Kalkulasi Money Management
            risiko_rp = modal_trading * (risiko_persen / 100)
            risk_per_share = entry - sl
            max_lot = int((risiko_rp / risk_per_share) / 100) if risk_per_share > 0 else 0
            
            # HTML Layout Persis Seperti V17.7 (Elegan, Rapi, Vertikal)
            html_v17_layout = f"""
            <!-- KARTU HEADER EMITEN -->
            <div style="background-color: #0A0D12; border: 1px solid #1F2430; border-radius: 8px; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h1 style="color: #FFF; font-size: 32px; margin: 0; font-weight: 800; line-height: 1.2;">{s.get('TICKER')}</h1>
                    <h3 style="color: #00C853; font-size: 18px; margin: 0; font-weight: 600;">Rp {int(harga):,}</h3>
                </div>
                <div style="text-align: right;">
                    <span style="color: #666; font-size: 9px; font-weight: 600; letter-spacing: 1px;">BANDAR STATUS</span><br>
                    <span style="color: #D4AF37; font-size: 14px; font-weight: 800;">{s.get('STATUS_BANDAR')}</span>
                </div>
            </div>
            
            <!-- METRIK ENTRY (VERTIKAL BERJAJAR RAPI) -->
            <div style="background-color: #0A0D12; border: 1px solid #1F2430; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 12px;">
                <span style="color: #666; font-size: 10px; font-weight: 600; letter-spacing: 1px;">🎯 ENTRY IDEAL</span><br>
                <span style="color: #FFF; font-size: 22px; font-weight: 800;">Rp {int(entry):,}</span>
            </div>
            
            <div style="background-color: #0A0D12; border: 1px solid #1F2430; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 12px;">
                <span style="color: #666; font-size: 10px; font-weight: 600; letter-spacing: 1px;">🚨 STOP LOSS</span><br>
                <span style="color: #FF3D00; font-size: 22px; font-weight: 800;">Rp {int(sl):,}</span>
            </div>
            
            <div style="background-color: #0A0D12; border: 1px solid #1F2430; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 20px;">
                <span style="color: #666; font-size: 10px; font-weight: 600; letter-spacing: 1px;">🚀 TP 1 (RR 1:1.5)</span><br>
                <span style="color: #00C853; font-size: 22px; font-weight: 800;">Rp {int(tp1):,}</span>
            </div>
            
            <!-- KARTU REKOMENDASI LOT (GOLD BORDER) -->
            <div style="border: 1px solid #D4AF37; background-color: rgba(212, 175, 55, 0.05); border-radius: 8px; padding: 20px; text-align: center;">
                <span style="color: #D4AF37; font-size: 10px; font-weight: 600; letter-spacing: 1px;">🛡️ MAX LOT SIZE (REKOMENDASI)</span><br>
                <h1 style="color: #D4AF37; font-size: 38px; margin: 10px 0; font-weight: 800; line-height: 1;">{max_lot} <span style="font-size: 16px;">LOT</span></h1>
                <span style="color: #888; font-size: 11px;">Berdasarkan risiko {risiko_persen}% dari modal</span>
            </div>
            """
            st.markdown(html_v17_layout, unsafe_allow_html=True)

    with tab_cluster:
        st.markdown("#### 🔥 TOP SETUP HARI INI")
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        df_setup = df_all[df_all['SETUP_GRADE'].str.contains("A\+") | df_all['SETUP_GRADE'].str.contains("JACKPOT")]
        if not df_setup.empty:
            st.dataframe(df_setup[['TICKER', 'HARGA', 'AREA BELI', 'TP1', 'STATUS_BANDAR']], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada Setup A+ hari ini berdasarkan data scan terakhir.")

    with tab_sop:
        st.markdown("### 📖 SOP J-G ULTIMATE V17.7")
        st.markdown("Panduan operasional resmi untuk membaca algoritma dan mengambil keputusan eksekusi trading.")
        st.markdown("---")
        
        st.markdown("#### 1. WPI (Whale Pressure Index) Score")
        st.markdown("WPI mengukur kekuatan tekanan pembeli dibandingkan penjual dalam satu hari perdagangan.")
        st.markdown("- **🟢 > 85 (Sangat Bagus):** Harga ditutup di pucuk tertinggi. Bandar memborong barang.")
        st.markdown("- **🟡 50 - 84 (Netral/Bagus):** Harga ditutup di area atas. Perlawanan seimbang.")
        st.markdown("- **🔴 < 50 (Waspada):** Harga ditutup di area terendah. Tekanan jual kuat.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. Bandar Flow & Price Action")
        st.markdown("- **🐋 AKUMULASI DASAR:** Volume meledak + Ekor bawah panjang di area harga rendah.")
        st.markdown("- **🟢 AKUMULASI AWAL:** Volume meledak + Harga naik normal.")
        st.markdown("- **🚀 MARK-UP BERINGAS:** Volume meledak + Harga naik + WPI > 70.")
        st.markdown("- **🩸 DISTRIBUSI PUCUK:** Volume meledak + Ekor atas panjang (Waspada bantingan).")
        st.markdown("- **💥 MARK-DOWN:** Volume meledak + Harga ditutup merah pekat.")
