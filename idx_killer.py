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
CACHE_FILE = "jihan_ghina_saham_cache_v18_lux.json"

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
# 1. LUXURY UI SETUP (V17.7 VIBES)
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate", page_icon="✨", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #E0E0E0 !important; }
    
    /* Perbaikan: Membuat header transparan agar tombol sidebar tetap bisa di-klik di HP */
    [data-testid="stHeader"] { background-color: transparent !important; } 
    
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
    section[data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #333 !important; }
    
    /* Sleek Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: 600; padding: 10px 15px; font-size: 13px; }
    .stTabs [aria-selected="true"] { color: #D4AF37; border-bottom: 2px solid #D4AF37; }
    
    /* Input Styling */
    div[data-baseweb="select"] > div, input { background-color: #000 !important; border: 1px solid #333 !important; color: #D4AF37 !important; font-weight: 600 !important; border-radius: 4px !important;}
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
        
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg: trailing_stop = harga_skg - (atr_skg * 2)
        
        risk_per_share = harga_skg - trailing_stop
        tp1 = harga_skg + (risk_per_share * 1.5)
        tp2 = harga_skg + (risk_per_share * 2.5)

        return {
            "TICKER": emiten.replace(".JK", ""), "HARGA": harga_skg, "AREA BELI": ema20_skg if harga_skg > ema20_skg else (low_20 + (harga_skg - low_20)*0.3), 
            "TRAILING STOP": trailing_stop, "TP1": tp1, "TP2": tp2, "WPI_SCORE": round(wpi_score, 1),
            "SEROK_SIGNAL": serok_signal, "STATUS_BANDAR": status_bandar, "SETUP_GRADE": setup_grade
        }
    except: return None

# ==========================================
# 3. SIDEBAR (MONEY MANAGEMENT ENGINE)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#D4AF37; font-weight:800; margin-bottom:0;'>✨ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:11px; margin-bottom:20px;'>LUXURY EDITION</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:12px; color:#E0E0E0; font-weight:bold; margin-bottom:10px;'>🛡️ MONEY MANAGEMENT</div>", unsafe_allow_html=True)
    modal_trading = st.number_input("Modal Trading (Rp)", min_value=100000, value=10000000, step=1000000, format="%d")
    risiko_persen = st.number_input("Risiko per Trade (%)", min_value=0.5, value=2.0, step=0.5, format="%.1f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 SCAN MARKET", use_container_width=True):
        st.session_state.raw_stocks = []
        my_bar = st.progress(0, text="Mengkalibrasi IHSG...")
        st.session_state.ihsg_data = fetch_ihsg_compass()
        scan_list = master_tickers[:40] # Bisa disesuaikan jumlahnya
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
# 4. SLEEK LIVE COMPASS (2-ROW LAYOUT ANTI TABRAK)
# ==========================================
ihsg = st.session_state.ihsg_data if hasattr(st.session_state, 'ihsg_data') else {"harga": 0, "change": 0, "trend": "NEUTRAL"}
ihsg_color = "#00C853" if ihsg.get("change", 0) > 0 else "#FF3D00"
ihsg_sign = "+" if ihsg.get("change", 0) > 0 else ""

html_live_ticker = f"""
<div style="background: #000; padding: 12px 15px; border-radius: 6px; border: 1px solid #333; margin-bottom: 15px;">
    <!-- Baris 1: Label & Jam -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="color: #888; font-size: 10px; font-family: sans-serif; font-weight: bold; letter-spacing: 1px;">MARKET COMPASS</span>
        <div style="display: flex; align-items: center; gap: 5px;">
            <div style="width: 6px; height: 6px; background-color: #00C853; border-radius: 50%; box-shadow: 0 0 5px #00C853; animation: blink 1.5s infinite;"></div>
            <strong id="live-clock" style="color: #D4AF37; font-size: 12px; font-family: monospace; letter-spacing: 1px;">--:--:--</strong>
        </div>
    </div>
    <!-- Baris 2: Data IHSG (Bebas memanjang) -->
    <div>
        <span style="color: #FFF; font-size: 16px; font-weight: 800; font-family: sans-serif;">IHSG : </span>
        <span style="color: {ihsg_color}; font-size: 16px; font-weight: 800; font-family: monospace;">{ihsg.get('harga', 0):,.2f}</span>
        <span style="color: {ihsg_color}; font-size: 12px; margin-left: 5px; font-family: monospace;">({ihsg_sign}{ihsg.get('change', 0):.2f}%)</span>
    </div>
</div>
<style>@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.2; }} 100% {{ opacity: 1; }} }}</style>
<script>
    setInterval(function() {{
        document.getElementById('live-clock').innerHTML = new Date().toLocaleTimeString('id-ID', {{ hour12: false }}) + " WIB";
    }}, 1000);
</script>
"""
components.html(html_live_ticker, height=90)

# ==========================================
# 5. MAIN DASHBOARD (ELEGANT LAYOUT)
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN MARKET' di menu sidebar (kiri atas) untuk memulai.")
else:
    tab_dash, tab_cluster, tab_sop = st.tabs(["✨ DASHBOARD", "🎯 CLUSTERING", "📖 PANDUAN & SOP"])
    
    with tab_dash:
        pilihan_ticker = st.selectbox("PENCARIAN EMITEN:", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0)
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            harga, entry, sl, tp1 = s.get('HARGA', 0), s.get('AREA BELI', 0), s.get('TRAILING STOP', 0), s.get('TP1', 0)
            
            # Perhitungan Money Management
            risiko_rp = modal_trading * (risiko_persen / 100)
            risk_per_share = entry - sl
            max_lot = int((risiko_rp / risk_per_share) / 100) if risk_per_share > 0 else 0
            
            # UI Render Menggunakan HTML Flexbox Murni
            html_dashboard = f"""
            <div style="background: transparent; margin-bottom: 20px;">
                <!-- HEADER EMITEN -->
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
                    <div>
                        <h1 style="margin: 0; font-size: 36px; color: #D4AF37; line-height: 1;">{s.get('TICKER')}</h1>
                        <h3 style="margin: 5px 0 0 0; color: #00C853; font-size: 20px;">Rp {int(harga):,}</h3>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; color: #888; font-size: 10px; font-weight: bold; letter-spacing: 1px;">STATUS BANDAR</p>
                        <h4 style="margin: 2px 0 0 0; color: #FFF; font-size: 16px;">{s.get('STATUS_BANDAR')}</h4>
                    </div>
                </div>
                
                <!-- METRICS GRID -->
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px;">
                    <div style="background: #000; border: 1px solid #222; border-radius: 6px; padding: 12px; text-align: center;">
                        <p style="margin: 0; font-size: 10px; color: #888; font-weight: bold; letter-spacing: 1px;">🎯 ENTRY</p>
                        <h3 style="margin: 5px 0 0 0; color: #FFF; font-size: 18px;">{int(entry):,}</h3>
                    </div>
                    <div style="background: #000; border: 1px solid #222; border-radius: 6px; padding: 12px; text-align: center;">
                        <p style="margin: 0; font-size: 10px; color: #888; font-weight: bold; letter-spacing: 1px;">🚨 STOP LOSS</p>
                        <h3 style="margin: 5px 0 0 0; color: #FF3D00; font-size: 18px;">{int(sl):,}</h3>
                    </div>
                    <div style="background: #000; border: 1px solid #222; border-radius: 6px; padding: 12px; text-align: center;">
                        <p style="margin: 0; font-size: 10px; color: #888; font-weight: bold; letter-spacing: 1px;">🚀 TP 1</p>
                        <h3 style="margin: 5px 0 0 0; color: #00C853; font-size: 18px;">{int(tp1):,}</h3>
                    </div>
                </div>
                
                <!-- MONEY MANAGEMENT CARD -->
                <div style="background: rgba(212, 175, 55, 0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 6px; padding: 15px; text-align: center;">
                    <p style="margin: 0; font-size: 11px; color: #D4AF37; font-weight: bold; letter-spacing: 1px;">🛡️ REKOMENDASI BELI MAKSIMAL</p>
                    <h1 style="margin: 10px 0; font-size: 42px; color: #D4AF37; font-weight: 800; line-height: 1;">{max_lot} <span style="font-size: 16px;">LOT</span></h1>
                    <p style="margin: 0; font-size: 11px; color: #888;">Maksimal kerugian dibatasi: <span style="color: #FF3D00;">Rp {int(risiko_rp):,}</span></p>
                </div>
            </div>
            """
            st.markdown(html_dashboard, unsafe_allow_html=True)

    with tab_cluster:
        st.markdown("#### 🔥 TOP SETUP HARI INI")
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        df_setup = df_all[df_all['SETUP_GRADE'].str.contains("A\+") | df_all['SETUP_GRADE'].str.contains("JACKPOT")]
        if not df_setup.empty:
            st.dataframe(df_setup[['TICKER', 'HARGA', 'AREA BELI', 'TP1', 'STATUS_BANDAR']], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada Setup A+ hari ini.")

    with tab_sop:
        st.markdown("### 📖 BUKU PANDUAN & SOP J-G ULTIMATE")
        st.markdown("Panduan operasional resmi untuk membaca algoritma dan mengambil keputusan eksekusi trading.")
        st.markdown("---")
        
        st.markdown("#### 1. WPI (Whale Pressure Index) Score")
        st.markdown("WPI adalah indikator untuk mengukur seberapa kuat tekanan pembeli (buyer) dibandingkan penjual (seller) dalam satu hari perdagangan.")
        st.markdown("- **Parameter / Rumus Asal:** Dihitung dari posisi Harga Penutupan (Close) relatif terhadap rentang pergerakan harga hari itu (High - Low).")
        st.markdown("- **Cara Membaca & Kode Warna:**")
        st.markdown("  - 🟢 **> 85 (Sangat Bagus):** Harga ditutup hampir di pucuk tertinggi hari itu. Artinya, bandar memborong barang sampai penutupan.")
        st.markdown("  - 🟡 **50 - 84 (Netral/Bagus):** Harga ditutup di area tengah/atas. Masih ada perlawanan seimbang.")
        st.markdown("  - 🔴 **< 50 (Waspada):** Harga ditutup di dekat area harga terendah. Tekanan jual kuat (dibanting seller).")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 2. Smart Money (Serok Signal)")
        st.markdown("Engine ini mendeteksi anomali saat market sedang panik/turun tajam, namun ada 'Uang Pintar' yang menampung barang.")
        st.markdown("- **Parameter Asal:** Sinyal `🐋 WHALE ABSORPTION` muncul JIKA 3 syarat ini terpenuhi bersamaan:")
        st.markdown("  1. **Harga di Dasar:** Harga berada maksimal 6% dari harga terendah dalam 20 hari terakhir.")
        st.markdown("  2. **Volume Meledak:** Volume transaksi melonjak >120% dari rata-rata 20 hari (SMA20 Volume).")
        st.markdown("  3. **Candlestick Rejection:** Panjang ekor bawah (Lower Shadow) > 1.5 kali panjang badan (Body) candle.")
        st.markdown("- **Penjelasan Hasil:** Ini adalah area spekulasi *Buy on Weakness* dengan probabilitas pantulan tinggi.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 3. Bandar Flow (Status Bandar)")
        st.markdown("Menggunakan metode Price & Volume Action (VPA) sebagai proksi pergerakan Bandar (karena data broker summary tidak tersedia di sumber publik).")
        st.markdown("- **Cara Membaca:**")
        st.markdown("  - **🐋 AKUMULASI DASAR:** Volume meledak + Ekor bawah panjang (Bandar serok di bawah).")
        st.markdown("  - **🟢 AKUMULASI AWAL:** Volume meledak + Harga naik normal.")
        st.markdown("  - **🚀 MARK-UP BERINGAS:** Volume meledak + Harga naik + WPI > 70 (Bandar kerek harga naik agresif).")
        st.markdown("  - **🩸 DISTRIBUSI PUCUK:** Volume meledak + Ekor atas panjang (Bandar jualan saat ritel FOMO).")
        st.markdown("  - **💥 MARK-DOWN:** Volume meledak + Harga ditutup merah pekat (Bandar buang barang).")
        st.markdown("  - **➖ NEUTRAL:** Volume transaksi biasa saja / di bawah rata-rata.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 4. Analisis Bid & Offer (Analogi Logika)")
        st.markdown("- **Apakah Bid & Offer ada di sistem ini?** Belum ada. Data Bid & Offer tertutup oleh sistem sekuritas lokal.")
        st.markdown("- **Analogi Logika (Cara Script Mengakali):** Karena tidak ada Bid/Offer, script menggunakan **Volume Spike & Shadow Analysis**. Kita tidak perlu tertipu melihat antrean Bid/Offer yang sering dipalsukan (Fake Bid/Offer) oleh bandar. Kita cukup melihat **Hasil Akhirnya (Volume & Harga Penutupan)**. Jika Bid dicabut dan harga dibanting, otomatis terbaca sebagai `💥 MARK-DOWN` atau membentuk ekor atas yang panjang.")
