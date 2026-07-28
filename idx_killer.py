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
# 0. REACTIVE ENGINE & PERSISTENT CACHE
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
# 1. LUXURY UI & EXTREME MOBILE CSS (RESTORED)
# ==========================================
st.set_page_config(page_title="JIHAN-GHINA Ultimate", page_icon="✨", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    [data-testid="stAppViewContainer"] { background-color: #050505 !important; color: #A1A1AA !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    
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
    
    /* Tabs Overhaul - Restored to classic style */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 15px;}
    .stTabs [data-baseweb="tab"] { color: #71717A; font-weight: 700; background: transparent; padding: 10px 5px; border: none; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;}
    .stTabs [aria-selected="true"] { color: #C6A87C; border-bottom: 2px solid #C6A87C;}
    
    /* Elegant Cards */
    .pro-card { 
        background: linear-gradient(145deg, #121214, #09090B);
        border: 1px solid #27272A; 
        border-radius: 12px; 
        padding: 16px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 12px;
    }
    
    .card-label { color: #C6A87C; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #27272A; padding-bottom: 8px;}
    
    .data-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 5px;}
    .data-label { font-size: 10px; color: #71717A; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; display:block;}
    .data-value { font-size: 15px; color: #FAFAFA; font-weight: 700; display:block;}
    
    .score-box { border: 1px solid #27272A; border-radius: 8px; padding: 12px; text-align: center; background: #050505;}
    .score-value { font-size: 28px; font-weight: 800; color: #C6A87C; line-height: 1; margin: 4px 0;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE & INDICATORS
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
    "RAJA", "HATM", "KRYA", "BSBK", "DATA", "NICL", "PAMG", "TRJA", "CARS", "BAPA", "KIJA", "DILD", "LPCK", "FWCT", "PURI", "SULI"
]
master_tickers = list(set([t.strip().upper() + ".JK" for t in MASTER_UNIVERSE]))

def get_waktu_wib(): return datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y - %H:%M")

def fetch_ihsg():
    try:
        tkr = yf.Ticker("^JKSE")
        hist = tkr.history(period="5d")
        if len(hist) >= 2:
            now, prev = float(hist['Close'].iloc[-1]), float(hist['Close'].iloc[-2])
            return {"val": now, "change": ((now - prev) / prev) * 100}
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
                close_now, vol_now = float(df_t['Close'].iloc[-1]), float(df_t['Volume'].iloc[-1])
                market_data.append({'Ticker': ticker, 'TransVal': close_now * vol_now})
            except: continue
            
        df_market = pd.DataFrame(market_data)
        # HAPUS FILTER KEJAM. Semua saham dengan volume masuk roster.
        top_liquid = df_market.nlargest(150, 'TransVal')['Ticker'].tolist()
        return list(set(top_liquid + master_tickers[:50]))[:200]
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
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    return np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1).rolling(period).mean()

def fetch_single_stock(emiten, mode_tf):
    try:
        kode = emiten.replace(".JK", "")
        tkr = yf.Ticker(emiten)
        df = tkr.history(period="1y", interval="1d")
        if df.empty or len(df) < 30: return None 
        
        df = df.ffill().dropna(subset=['Close'])
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
        
        harga_skg = float(df['Close'].iloc[-1])
        open_skg = float(df['Open'].iloc[-1])
        high_skg = float(df['High'].iloc[-1])
        low_skg = float(df['Low'].iloc[-1])
        vol_skg = float(df['Volume'].iloc[-1])
        vol_sma20 = float(df['Vol_SMA20'].iloc[-1])
        adtv_20 = float(df['Turnover'].rolling(20).mean().iloc[-1])
        
        is_bullish = harga_skg >= open_skg
        body_size = abs(open_skg - harga_skg)
        lower_shadow = (open_skg if is_bullish else harga_skg) - low_skg
        upper_shadow = high_skg - (harga_skg if is_bullish else open_skg)
        
        is_vol_spike = vol_skg > (vol_sma20 * 1.5)
        is_bull_trap = is_vol_spike and (upper_shadow > body_size * 1.5) and not is_bullish
        is_fake_pump = is_vol_spike and (upper_shadow > body_size * 2) and is_bullish
        
        low_20 = float(df['Low'].tail(20).min())
        is_near_bottom = (harga_skg - low_20) / low_20 <= 0.08
        
        if is_bull_trap or is_fake_pump: status_bandar = "🚨 BULL TRAP / DISTRIBUSI"
        elif is_vol_spike and lower_shadow > (body_size * 1.5) and is_near_bottom: status_bandar = "🐋 AKUMULASI DASAR"
        elif is_vol_spike and is_bullish and upper_shadow < body_size: status_bandar = "🚀 MARK-UP SOLID"
        elif is_vol_spike and not is_bullish: status_bandar = "🩸 DISTRIBUSI MASIF"
        else: status_bandar = "➖ NEUTRAL"

        wpi_score = ((harga_skg - low_skg) / (high_skg - low_skg)) * 100 if high_skg > low_skg else 50.0
        if is_bull_trap or is_fake_pump: wpi_score = max(0, wpi_score - 40) 
        
        trailing_stop = float(df['Chandelier_Exit'].iloc[-1])
        if pd.isna(trailing_stop) or trailing_stop >= harga_skg: trailing_stop = harga_skg - (float(df['ATR'].iloc[-1]) * 2) 

        info = tkr.info if hasattr(tkr, 'info') and tkr.info else {}
        return {
            "TICKER": kode, "HARGA": harga_skg, "MA20": float(df['EMA20'].iloc[-1]), "MA50": float(df['SMA50'].iloc[-1]), 
            "AREA BELI": low_20 + (harga_skg - low_20)*0.3, "TRAILING STOP": trailing_stop, 
            "WPI_SCORE": round(wpi_score, 1), "STATUS_BANDAR": status_bandar, 
            "PER": round(info.get('trailingPE', 0.0), 2) if info.get('trailingPE') else 0.0, 
            "ROE": round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 0.0,
            "YIELD": f"{round(info.get('dividendYield', 0)*100, 2) if info.get('dividendYield') else 0}%", 
            "PBV": round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else 0.0, 
            "RET_1D": ((harga_skg - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2]) * 100), 
            "VOLUME": vol_skg, "VOL_SMA20": vol_sma20, "IS_SPIKE": is_vol_spike, "ADTV_20": adtv_20,
            "NAME": info.get('longName', kode), "SECTOR": info.get('sector', '-'),
            "MACD_BULLISH": float(df['MACD'].iloc[-1]) > float(df['Signal_Line'].iloc[-1])
        }
    except Exception as e: return None

# ==========================================
# 3. SIDEBAR (CLASSIC LUXURY)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#C6A87C; font-size:16px; font-weight:800; margin-bottom:0;'>✨ J-G ULTIMATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#71717A; font-size:9px; letter-spacing:1px; margin-bottom:20px;'>EDITION V18.0.1</p>", unsafe_allow_html=True)
    
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
        
        radar_bar = st.progress(0, text="Membaca Market...")
        st.session_state.ihsg_data = fetch_ihsg()
        dynamic_tickers = get_dynamic_market_roster()
        
        for i, t in enumerate(dynamic_tickers):
            radar_bar.progress((i + 1) / len(dynamic_tickers), text=f"{t} ({i+1}/{len(dynamic_tickers)})")
            data = fetch_single_stock(t, tf_pilihan)
            if data: st.session_state.raw_stocks.append(data)
            gc.collect() 
        radar_bar.empty()
        st.session_state.last_update = get_waktu_wib()
        try:
            with open(CACHE_FILE, "w") as f: 
                json.dump({"raw_stocks": st.session_state.raw_stocks, "last_update": st.session_state.last_update, "ihsg": st.session_state.ihsg_data}, f)
        except: pass
        st.rerun()
        
    if st.session_state.last_update:
        st.markdown(f"<div style='font-size:8px; color:#71717A; text-align:center; margin-top:20px;'>Last Update:<br>{st.session_state.last_update}</div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN LAYOUT (RESTORED CLASSIC TABS)
# ==========================================
if not st.session_state.raw_stocks:
    st.info("👈 Tekan tombol '🔄 SCAN' di sidebar untuk memulai.")
else:
    tab_scan, tab_export, tab_sop = st.tabs(["📊 SCANNER", "📥 EXPORT", "📖 SOP"])
    
    # ------------------------------------------
    # TAB 1: SCANNER (Funda, Smart Money, Analisa)
    # ------------------------------------------
    with tab_scan:
        ihsg = st.session_state.ihsg_data
        ihsg_val, ihsg_change = ihsg.get("val", 0), ihsg.get("change", 0)
        
        # IHSG BANNERS & SELECTOR
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #18181B, #09090B); border: 1px solid #3F3F46; border-radius: 10px; padding: 12px 16px; margin-bottom: 15px; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:10px; color:#A1A1AA; font-weight:700;">🇲🇨 IHSG (COMPOSITE)</div>
            <div style="font-size:16px; font-weight:800; color:{'#10B981' if ihsg_change >= 0 else '#EF4444'};">{ihsg_val:,.2f} ({'+' if ihsg_change>=0 else ''}{ihsg_change:.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

        pilihan_ticker = st.selectbox("Pilih Emiten", [s.get('TICKER', '') for s in st.session_state.raw_stocks if 'TICKER' in s], index=0, label_visibility="collapsed")
        s = next((item for item in st.session_state.raw_stocks if item.get("TICKER") == pilihan_ticker), None)
        
        if s:
            # Peringatan Gorengan (Tanpa Menghapus Data)
            is_gorengan = s.get('ADTV_20', 0) < 3_000_000_000
            warning_html = f"""<div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 6px; padding: 8px; margin-bottom: 12px; text-align:center; color:#EF4444; font-size:11px; font-weight:700;">⚠️ PERINGATAN: LIKUIDITAS RENDAH (ADTV < 3 Miliar). RAWAN GORENGAN BANDAR!</div>""" if is_gorengan else ""
            
            st.markdown(warning_html, unsafe_allow_html=True)
            
            # HEADER IDENTITAS
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <div>
                    <h2 style="margin:0; color:#FAFAFA; font-size:24px; font-weight:800;">{s.get('TICKER', '')}</h2>
                    <p style="margin:0; color:#A1A1AA; font-size:12px;">{s.get('NAME', '')} • {s.get('SECTOR', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # SMART MONEY & BANDARMOLOGI
            vol_spike_text = "🔥 TERDETEKSI" if s.get('IS_SPIKE', False) else "➖ NORMAL"
            vol_spike_color = "#10B981" if s.get('IS_SPIKE', False) else "#71717A"
            bandar_flow = s.get('STATUS_BANDAR', 'NEUTRAL')
            bf_color = '#EF4444' if 'DISTRIBUSI' in bandar_flow or 'TRAP' in bandar_flow else ('#10B981' if 'AKUMULASI' in bandar_flow or 'MARK-UP' in bandar_flow else '#C6A87C')
            
            col_sm1, col_sm2 = st.columns([1, 1])
            with col_sm1:
                st.markdown(f"""
                <div class="pro-card" style="height:100%;">
                    <div class="card-label">🐋 SMART MONEY & BANDARMOLOGI</div>
                    <div class="data-grid">
                        <div><span class="data-label">BANDAR FLOW</span><span class="data-value" style="color:{bf_color}">{bandar_flow}</span></div>
                        <div><span class="data-label">VOLUME SPIKE</span><span class="data-value" style="color:{vol_spike_color}">{vol_spike_text}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_sm2:
                st.markdown(f"""
                <div class="score-box" style="height:100%; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:11px; color:#71717A; font-weight:700; text-transform:uppercase;">WPI SCORE (STRENGTH)</div>
                    <div class="score-value" style="color: {'#EF4444' if s.get('WPI_SCORE', 0) < 40 else '#C6A87C'};">{s.get('WPI_SCORE', 0):.1f}</div>
                </div>
                """, unsafe_allow_html=True)

            # ANALISA HARGA & TEKNIKAL
            st.markdown(f"""
            <div class="pro-card">
                <div class="card-label">📈 ANALISA HARGA & TEKNIKAL</div>
                <div class="data-grid" style="grid-template-columns: repeat(4, 1fr);">
                    <div><span class="data-label">HARGA SAAT INI</span><span class="data-value" style="font-size:18px;">Rp {int(s.get('HARGA', 0)):,}</span></div>
                    <div><span class="data-label">MA 20 (SUPPORT 1)</span><span class="data-value">Rp {int(s.get('MA20', 0)):,}</span></div>
                    <div><span class="data-label">MA 50 (SUPPORT 2)</span><span class="data-value">Rp {int(s.get('MA50', 0)):,}</span></div>
                    <div><span class="data-label">TRAILING STOP</span><span class="data-value" style="color:#EF4444;">Rp {int(s.get('TRAILING STOP', 0)):,}</span></div>
                </div>
                <div style="margin-top:15px; padding-top:10px; border-top:1px solid #27272A; display:flex; justify-content:space-between;">
                    <div><span class="data-label">TREND MACD</span><span class="data-value" style="color:{'#10B981' if s.get('MACD_BULLISH') else '#EF4444'};">{'BULLISH (UPTREND)' if s.get('MACD_BULLISH') else 'BEARISH (DOWNTREND)'}</span></div>
                    <div style="text-align:right;"><span class="data-label">RATA-RATA TRANSAKSI (ADTV)</span><span class="data-value">Rp {s.get('ADTV_20', 0)/1e9:.1f} Miliar/Hari</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FUNDAMENTAL
            st.markdown(f"""
            <div class="pro-card">
                <div class="card-label">🏢 FUNDAMENTAL & VALUASI</div>
                <div class="data-grid" style="grid-template-columns: repeat(4, 1fr);">
                    <div><span class="data-label">P/E RATIO</span><span class="data-value">{s.get('PER', 0)}x</span></div>
                    <div><span class="data-label">PBV</span><span class="data-value">{s.get('PBV', 0)}x</span></div>
                    <div><span class="data-label">ROE</span><span class="data-value">{s.get('ROE', 0)}%</span></div>
                    <div><span class="data-label">DIVIDEND YIELD</span><span class="data-value" style="color:#C6A87C;">{s.get('YIELD', '0%')}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: EXPORT
    # ------------------------------------------
    with tab_export:
        st.markdown("<h4 style='color:#C6A87C; font-size:14px; margin-bottom:15px;'>📥 Ekspor Watchlist</h4>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.raw_stocks)
        if not df_all.empty:
            df_export = df_all[['TICKER', 'NAME', 'HARGA', 'MA20', 'TRAILING STOP', 'STATUS_BANDAR']]
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 DOWNLOAD CSV (EXCEL)", data=csv_data, file_name=f"JG_Ultimate_Watchlist.csv", mime="text/csv", use_container_width=True)

    # ------------------------------------------
    # TAB 3: SOP (Standar Operasional Prosedur) & Risk Calculator
    # ------------------------------------------
    with tab_sop:
        st.markdown("""
        <div class="pro-card">
            <h4 style="color:#C6A87C; margin-top:0;">📖 SOP TRADING AMAN</h4>
            <ol style="color:#A1A1AA; font-size:13px; padding-left:15px; line-height:1.6;">
                <li><b>Cek Tab SCANNER:</b> Pastikan tidak ada stempel merah (Gorengan/ADTV rendah).</li>
                <li><b>Lihat Smart Money:</b> Prioritaskan beli hanya saat Bandar Flow berstatus <span style="color:#10B981; font-weight:bold;">AKUMULASI DASAR</span> atau <span style="color:#10B981; font-weight:bold;">MARK-UP SOLID</span>.</li>
                <li><b>Analisa Harga:</b> Usahakan harga saat ini dekat dengan MA20 (Support). Jangan kejar harga jika sudah terlalu jauh dari MA20.</li>
                <li><b>Wajib Disiplin:</b> Pasang Auto-Order (Jual Otomatis) di aplikasi sekuritas Anda tepat di angka <span style="color:#EF4444; font-weight:bold;">TRAILING STOP / CUT LOSS</span>.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color:#3B82F6; font-size:14px; margin-top:20px; margin-bottom:10px;'>🛡️ KALKULATOR MANAJEMEN RISIKO (SOP)</h4>", unsafe_allow_html=True)
        calc_c1, calc_c2 = st.columns(2)
        with calc_c1:
            modal_rp = st.number_input("💰 Total Modal Anda (Rp)", min_value=1000000, value=10000000, step=1000000, key="modal_sop")
        with calc_c2:
            risk_pct = st.number_input("📉 Siap Rugi Berapa % dari Modal?", min_value=0.5, max_value=5.0, value=1.0, step=0.5, key="risk_sop")
        
        if s: # Jika ada saham yang dipilih di tab scanner
            harga_aktif = float(s.get('HARGA', 0))
            sl_aktif = float(s.get('TRAILING STOP', 0))
            risk_amount = modal_rp * (risk_pct / 100)
            jarak_sl_rp = harga_aktif - sl_aktif
            
            if jarak_sl_rp > 0:
                max_lot = int((risk_amount / jarak_sl_rp) / 100)
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3B82F6; border-radius: 8px; padding: 15px; margin-top: 15px; text-align:center;">
                    <span style="font-size:12px; color:#A1A1AA;">Untuk saham <b>{s.get('TICKER')}</b> (Harga Rp {int(harga_aktif):,} | Cut Loss Rp {int(sl_aktif):,})</span><br>
                    <span style="font-size:11px; color:#FAFAFA; font-weight:700;">MAKSIMAL PEMBELIAN SESUAI SOP ADALAH:</span><br>
                    <span style="font-size:32px; color:#3B82F6; font-weight:800;">{max_lot:,} LOT</span><br>
                    <span style="font-size:11px; color:#EF4444; font-weight:700;">Jika Cut Loss tersentuh, kerugian Anda pasti terkunci di Rp {int(risk_amount):,}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Harga saat ini sudah di bawah titik Stop Loss. JANGAN DIBELI!")
