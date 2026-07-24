import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="JIHAN-GHINA Ultimate v18.5",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (Untuk UI Cards & Warna) ---
st.markdown("""
<style>
.big-card-same {
    background-color: #0E1117; padding: 20px; border-radius: 10px;
    text-align: center; border: 1px solid #00E676; margin-bottom: 10px;
}
.big-card-heal {
    background-color: #0E1117; padding: 20px; border-radius: 10px;
    text-align: center; border: 1px solid #FF5252; margin-bottom: 10px;
}
.metric-card {
    background-color: #161A25; padding: 15px; border-radius: 8px;
    text-align: center; border: 1px solid #1E2329;
}
.metric-value { font-size: 24px; font-weight: bold; color: #F5C518; }
.metric-label { font-size: 10px; color: #8B949E; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (Mencegah Reset Data Otomatis) ---
if 'eksekusi_mode' not in st.session_state:
    st.session_state.eksekusi_mode = "🔴 SAME"

# --- 4. ENGINE CACHING & FILTERING LOGIC ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_financial_data(ticker_symbol):
    """Mengambil data Quarterly dari YFinance dengan Cache 1 Jam"""
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.quarterly_income_stmt, stock.quarterly_balance_sheet, stock.quarterly_cash_flow
    except Exception:
        return None, None, None

@st.cache_data(ttl=300)
def get_master_sniper_data():
    """Master Data Engine (Ganti dengan koneksi API asli Anda)"""
    data = {
        "EMITEN": ["PANI", "BBCA", "BREN", "AMMN", "CUAN", "BRPT", "BBRI", "BMRI", "TLKM", "BBNI", "GOTO", "ANTM"],
        "HARGA": [6350, 9800, 8200, 8900, 7500, 1200, 4700, 6100, 3100, 4900, 50, 1400],
        "1D GAIN (%)": ["+0.79%", "+0.78%", "-1.20%", "+0.57%", "+0.51%", "-2.30%", "+0.28%", "+0.24%", "-1.50%", "+0.00%", "-3.00%", "-0.50%"],
        "SEROK BAWAH 🎯": ["➖", "➖", "🟢 OVERSOLD REBOUND", "➖", "➖", "🟢 OVERSOLD REBOUND", "➖", "➖", "🟢 OVERSOLD REBOUND", "➖", "🟢 OVERSOLD REBOUND", "🟢 OVERSOLD REBOUND"],
        "SNIPER CROSS VALIDATION": ["🔥 STRONG BUY", "✅ BUY", "⏳ WAIT", "✅ BUY", "✅ BUY", "⏳ WAIT", "✅ BUY", "✅ BUY", "⏳ WAIT", "⏳ WAIT", "🔥 STRONG REBOUND", "⏳ WAIT"]
    }
    return pd.DataFrame(data)

def filter_data_by_mode(df, mode):
    """Logika Overpowered: Filter data otomatis berdasarkan Mode"""
    if mode == "🔴 SAME":
        # Mode SAME: Cari yang sedang Uptrend / Strong Buy (Gain positif)
        filtered_df = df[df['1D GAIN (%)'].str.contains('\+')].copy()
    else:
        # Mode HEAL: Cari yang sedang Downtrend tapi ada sinyal Oversold Rebound
        filtered_df = df[df['SEROK BAWAH 🎯'].str.contains('OVERSOLD REBOUND')].copy()
    
    return filtered_df.head(10) # Kembalikan Top 10

def render_yfinance_chart(df, title, color_theme):
    """Render Chart Plotly Statis Anti-Geser"""
    fig = go.Figure()
    if df is not None and not df.empty:
        df_plot = df.head(3).T.sort_index()
        for col in df_plot.columns:
            fig.add_trace(go.Bar(
                x=df_plot.index.strftime('%Y-%m') if isinstance(df_plot.index, pd.DatetimeIndex) else df_plot.index, 
                y=df_plot[col], name=str(col)
            ))
            
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=color_theme)), barmode='group',
        dragmode=False, hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(fixedrange=True, showgrid=False), yaxis=dict(fixedrange=True, showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    return fig

# --- 5. BAGIAN ATAS: EKSEKUSI PRESISI & ALGO DECISION ---
st.markdown("<p style='color:#00E676; font-weight:bold; font-size:14px;'>PILIH TARGET EKSEKUSI PRESISI (FILTER CERDAS AKTIF):</p>", unsafe_allow_html=True)

# Toggle Interaktif
st.session_state.eksekusi_mode = st.radio(
    "Mode Eksekusi", ["🔴 SAME", "⚫ HEAL"],
    index=0 if st.session_state.eksekusi_mode == "🔴 SAME" else 1,
    horizontal=True, label_visibility="collapsed"
)

# UI Berubah Dinamis Tergantung Mode
if st.session_state.eksekusi_mode == "🔴 SAME":
    st.markdown("""
    <div class="big-card-same">
        <p style="color:#8B949E; font-size:12px; font-weight:bold; margin-bottom:5px;">💻 DYNAMIC ALGO DECISION</p>
        <h2 style="color:#00E676; margin:0px; font-size:28px;">🚀 RIDING THE TREND (FOLLOW MOMENTUM)</h2>
        <p style="color:#00E676; font-size:14px; margin-top:5px; font-weight:bold;">🎯 SETUP: STRONG BUY / BREAKOUT</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="big-card-heal">
        <p style="color:#8B949E; font-size:12px; font-weight:bold; margin-bottom:5px;">💻 DYNAMIC ALGO DECISION</p>
        <h2 style="color:#F5C518; margin:0px; font-size:28px;">🎯 JACKPOT (SEROK BAWAH)</h2>
        <p style="color:#F5C518; font-size:14px; margin-top:5px; font-weight:bold;">🎯 SETUP: OVERSOLD RECOVERY</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-label">HARGA AKTIF (SIMULASI)</div><div class="metric-value">298</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-label">AREA BELI ALGORITMA</div><div class="metric-value">290 - 296</div></div>', unsafe_allow_html=True)

st.write("")

# --- 6. TABS DASHBOARD UTAMA ---
tab_sniper, tab_invest = st.tabs(["🎯 Top 10 Sniper Utama", "💼 Investment & Financials"])

# ==========================================
# TAB 1: TOP 10 SNIPER UTAMA
# ==========================================
with tab_sniper:
    st.subheader(f"🛰️ Target Sniper Utama ({st.session_state.eksekusi_mode} MODE)")
    
    # Ambil Data Master & Filter Berdasarkan Mode
    df_master = get_master_sniper_data()
    df_filtered = filter_data_by_mode(df_master, st.session_state.eksekusi_mode)
    
    st.dataframe(df_filtered, use_container_width=True, hide_index=True, height=400)
    st.button("📥 Download Master Excel (Filtered Data)")

# ==========================================
# TAB 2: INVESTMENT & FINANCIALS
# ==========================================
with tab_invest:
    st.subheader("📊 Quarterly Financial Statements (YFinance Style)")
    st.markdown("<p style='color:#8B949E; font-size:14px;'><i>Chart statis (drag/zoom dinonaktifkan) agar layar tidak tergeser saat di-scroll di perangkat mobile.</i></p>", unsafe_allow_html=True)
    
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        ticker_input = st.text_input("Kode Emiten (Gunakan .JK):", value="BBCA.JK", max_chars=10)
    
    if ticker_input:
        with st.spinner("Menarik laporan keuangan terbaru..."):
            inc_stmt, bal_sheet, cash_flow = get_financial_data(ticker_input.upper())
            st.divider()
            chart_config = {'displayModeBar': False} 
            
            if inc_stmt is not None and not inc_stmt.empty:
                st.plotly_chart(render_yfinance_chart(inc_stmt, "📈 Income Statement (Quarterly)", "#00E676"), use_container_width=True, config=chart_config)
            else:
                st.info("Data Income Statement belum tersedia.")
                
            if bal_sheet is not None and not bal_sheet.empty:
                st.plotly_chart(render_yfinance_chart(bal_sheet, "⚖️ Balance Sheet (Quarterly)", "#29B6F6"), use_container_width=True, config=chart_config)
            else:
                st.info("Data Balance Sheet belum tersedia.")
                
            if cash_flow is not None and not cash_flow.empty:
                st.plotly_chart(render_yfinance_chart(cash_flow, "💵 Cash Flow (Quarterly)", "#FFA726"), use_container_width=True, config=chart_config)
            else:
                st.info("Data Cash Flow belum tersedia.")

# --- 7. FOOTER ---
st.divider()
st.markdown("""
<div style='text-align: center;'>
    <p style='color: #8B949E; font-size: 14px; font-weight: bold; margin-bottom: 0;'>⚡ JIHAN-GHINA ENGINE • INSTITUTIONAL MASTERPIECE v18.5</p>
    <p style='color: #8B949E; font-size: 12px; margin-top: 0;'>(Super OP Edition - Dynamic Smart Filter & Anti-Reset System)</p>
</div>
""", unsafe_allow_html=True)
