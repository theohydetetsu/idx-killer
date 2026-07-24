import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. KONFIGURASI HALAMAN (SIDEBAR & LUXURY LAYOUT) ---
st.set_page_config(
    page_title="JIHAN-GHINA Ultimate v20.0", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LUXURY CSS (Tema Gelap ala Aplikasi Trading Premium) ---
st.markdown("""
<style>
    /* Latar belakang aplikasi */
    .stApp {
        background-color: #0A0D14;
    }
    
    /* Sembunyikan header bawaan Streamlit agar lebih bersih */
    header {visibility: hidden;}

    /* Kartu Premium SAME (Trend) */
    .premium-card-same {
        background: linear-gradient(145deg, #0D1B1A, #0A0D14);
        border-radius: 16px; padding: 24px; text-align: center;
        border: 1px solid rgba(0, 230, 118, 0.2);
        box-shadow: 0 8px 32px rgba(0, 230, 118, 0.05); margin-bottom: 20px;
    }
    
    /* Kartu Premium HEAL (Recovery) */
    .premium-card-heal {
        background: linear-gradient(145deg, #1A1311, #0A0D14);
        border-radius: 16px; padding: 24px; text-align: center;
        border: 1px solid rgba(255, 171, 0, 0.2);
        box-shadow: 0 8px 32px rgba(255, 171, 0, 0.05); margin-bottom: 20px;
    }

    /* Kartu Metrik Angka */
    .luxury-metric {
        background-color: #121620; border-radius: 12px; padding: 16px;
        text-align: center; border: 1px solid #1C2333;
    }
    .lux-label {
        color: #8E9BAE; font-size: 11px; font-weight: 600; letter-spacing: 1px;
        text-transform: uppercase; margin-bottom: 5px;
    }
    .lux-value {
        color: #FFFFFF; font-size: 26px; font-weight: 700;
    }
    .lux-value-accent {
        color: #FFB300; font-size: 26px; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (ANTI-RESET DATA) ---
if 'mode_eksekusi' not in st.session_state:
    st.session_state.mode_eksekusi = "SAME"

# --- 4. ENGINE CACHING (ANTI-THROTTLING) ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_financial_data(ticker_symbol):
    """Mengambil data Quarterly dari YFinance (Cache 1 Jam)"""
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.quarterly_income_stmt, stock.quarterly_balance_sheet, stock.quarterly_cash_flow
    except Exception:
        return None, None, None

@st.cache_data(ttl=300)
def get_top_10_sniper_data():
    """
    DUMMY DATA: Ganti bagian ini dengan engine kalkulasi momentum aslinya.
    Ditambahkan beberapa data negatif agar filter Serok Bawah terlihat berfungsi.
    """
    data = {
        "EMITEN": ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNVR", "ICBP", "INDF", "AMMN", "GOTO", "PANI"],
        "HARGA": [9800, 4700, 6100, 4900, 3100, 5200, 2400, 10500, 6200, 8900, 50, 6350],
        "1D GAIN (%)": ["+0.79%", "+0.78%", "+0.74%", "+0.57%", "-1.50%", "+0.30%", "-2.00%", "+0.24%", "+0.00%", "+0.00%", "-3.00%", "+1.20%"],
        "SEROK BAWAH 🎯": ["➖ TDK ADA SEROK", "➖ TDK ADA SEROK", "➖ TDK ADA SEROK", "➖ TDK ADA SEROK", "🟢 OVERSOLD REBOUND", "➖ TDK ADA SEROK", "🟢 OVERSOLD REBOUND", "➖ TDK ADA SEROK", "🟢 OVERSOLD REBOUND", "➖ TDK ADA SEROK", "🟢 OVERSOLD REBOUND", "➖ TDK ADA SEROK"],
        "SNIPER CROSS VALIDATION": ["✅ STRONG BUY", "⏳ WAIT", "✅ BUY", "⏳ WAIT", "❌ REJECT", "⏳ WAIT", "✅ BUY", "⏳ WAIT", "✅ STRONG BUY", "⏳ WAIT", "🔥 REBOUND", "🔥 STRONG BUY"]
    }
    return pd.DataFrame(data)

def filter_data_by_mode(df, mode):
    """Logika pemisah data otomatis berdasarkan mode eksekusi"""
    if mode == "SAME":
        filtered_df = df[df['1D GAIN (%)'].str.contains('\+')].copy()
    else:
        filtered_df = df[df['SEROK BAWAH 🎯'].str.contains('REBOUND')].copy()
    
    return filtered_df.head(10)

def render_yfinance_chart(df, title, base_color):
    """Membuat chart Plotly statis (anti-geser di HP) dengan Luxury Theme"""
    fig = go.Figure()
    
    if df is not None and not df.empty:
        df_plot = df.head(3).T.sort_index() 
        
        # Format X-Axis agar rapi
        if isinstance(df_plot.index, pd.DatetimeIndex):
            x_labels = df_plot.index.strftime('%b %Y')
        else:
            x_labels = df_plot.index

        # Palet warna turunan dari base_color agar elegan
        colors = [base_color, '#8E9BAE', '#4A5568']
        
        for i, col in enumerate(df_plot.columns):
            fig.add_trace(go.Bar(
                x=x_labels, 
                y=df_plot[col], 
                name=str(col),
                marker_color=colors[i % len(colors)],
                marker_line_width=0
            ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#FFFFFF")),
        barmode='group',
        dragmode=False,         # MATIKAN fitur geser/drag (Kunci utama untuk HP)
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1,
            font=dict(color="#8E9BAE")
        ),
        xaxis=dict(
            fixedrange=True,    # Kunci sumbu X
            showgrid=False, type='category', 
            tickangle=0, tickfont=dict(color="#8E9BAE")
        ),
        yaxis=dict(
            fixedrange=True,    # Kunci sumbu Y
            showgrid=True,
            gridcolor='#1C2333', zeroline=False,
            tickfont=dict(color="#8E9BAE")
        ),
        bargap=0.2, bargroupgap=0.1
    )
    return fig

# --- 5. SIDEBAR (KONTROL UTAMA & NAVIGASI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #FFFFFF;'>⚡ JIHAN-GHINA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8E9BAE; font-size: 13px;'>Institutional Terminal v20.0</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("<p style='color: #FFFFFF; font-weight: 600; font-size: 14px;'>PILIH MODE EKSEKUSI:</p>", unsafe_allow_html=True)
    
    # Tombol Mode Eksekusi
    if st.button("🚀 MODE SAME (Trend)", use_container_width=True, type="primary" if st.session_state.mode_eksekusi == "SAME" else "secondary"):
        st.session_state.mode_eksekusi = "SAME"
        st.rerun()
        
    if st.button("🎯 MODE HEAL (Serok Bawah)", use_container_width=True, type="primary" if st.session_state.mode_eksekusi == "HEAL" else "secondary"):
        st.session_state.mode_eksekusi = "HEAL"
        st.rerun()
        
    st.divider()
    st.markdown("<p style='color: #8E9BAE; font-size: 12px;'>Sistem pemantauan otomatis aktif tanpa reset data manual saat mode API dijalankan.</p>", unsafe_allow_html=True)

# --- 6. AREA DASHBOARD UTAMA ---
st.markdown("<h3 style='color: #FFFFFF; font-weight: 700;'>💎 MARKET INTELLIGENCE <span style='color: #8E9BAE; font-weight: 400; font-size: 16px;'>| Dashboard</span></h3>", unsafe_allow_html=True)
st.write("")

# Dynamic Algo Card
if st.session_state.mode_eksekusi == "SAME":
    st.markdown("""
    <div class="premium-card-same">
        <p style="color:#00E676; font-size:12px; font-weight:600; letter-spacing: 2px; margin-bottom:5px;">● ACTIVE ALGO: RIDING THE TREND</p>
        <h2 style="color:#FFFFFF; margin:0px; font-size:26px;">MOMENTUM BREAKOUT & STRONG BUY</h2>
        <p style="color:#8E9BAE; font-size:13px; margin-top:5px;">Menyaring emiten dengan tenaga dorong kenaikan harga yang kuat.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="premium-card-heal">
        <p style="color:#FFAB00; font-size:12px; font-weight:600; letter-spacing: 2px; margin-bottom:5px;">● ACTIVE ALGO: JACKPOT RECOVERY</p>
        <h2 style="color:#FFFFFF; margin:0px; font-size:26px;">OVERSOLD REBOUND (SEROK BAWAH)</h2>
        <p style="color:#8E9BAE; font-size:13px; margin-top:5px;">Menyaring emiten diskon yang siap memantul naik kembali.</p>
    </div>
    """, unsafe_allow_html=True)

# Metrik Harga Simulasi
col_met1, col_met2 = st.columns(2)
with col_met1:
    st.markdown('<div class="luxury-metric"><div class="lux-label">HARGA AKTIF (SIMULASI)</div><div class="lux-value">298</div></div>', unsafe_allow_html=True)
with col_met2:
    st.markdown('<div class="luxury-metric"><div class="lux-label">AREA BELI TARGET</div><div class="lux-value-accent">290 - 296</div></div>', unsafe_allow_html=True)

st.write("")

# --- 7. TABS NAVIGASI DATA ---
tab_sniper, tab_invest = st.tabs(["🎯 Top 10 Sniper Utama", "💼 Investment & Financials"])

# ==========================================
# TAB 1: TOP 10 SNIPER UTAMA
# ==========================================
with tab_sniper:
    # Ambil data lalu difilter sesuai mode
    df_master = get_top_10_sniper_data()
    df_filtered = filter_data_by_mode(df_master, st.session_state.mode_eksekusi)
    
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    st.button("📥 Download Master Excel (Filtered Data)")

# ==========================================
# TAB 2: INVESTMENT & FINANCIALS
# ==========================================
with tab_invest:
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        ticker_input = st.text_input("Kode Emiten (Gunakan .JK):", value="BBCA.JK", max_chars=10)
    
    if ticker_input:
        with st.spinner("Mengunduh laporan keuangan terbaru..."):
            inc_stmt, bal_sheet, cash_flow = get_financial_data(ticker_input.upper())
            st.divider()
            
            # Setting displayModeBar=False untuk bersih dari menu bawaan plotly
            chart_config = {'displayModeBar': False}
            
            if inc_stmt is not None and not inc_stmt.empty:
                st.plotly_chart(render_yfinance_chart(inc_stmt, "📈 Income Statement (Quarterly)", "#00E676"), use_container_width=True, config=chart_config)
            else:
                st.info("Data Income Statement belum tersedia untuk emiten ini.")
                
            if bal_sheet is not None and not bal_sheet.empty:
                st.plotly_chart(render_yfinance_chart(bal_sheet, "⚖️ Balance Sheet (Quarterly)", "#29B6F6"), use_container_width=True, config=chart_config)
            else:
                st.info("Data Balance Sheet belum tersedia untuk emiten ini.")
                
            if cash_flow is not None and not cash_flow.empty:
                st.plotly_chart(render_yfinance_chart(cash_flow, "💵 Cash Flow (Quarterly)", "#FFA726"), use_container_width=True, config=chart_config)
            else:
                st.info("Data Cash Flow belum tersedia untuk emiten ini.")

# --- 8. FOOTER ---
st.markdown("""
<div style='text-align: center; margin-top: 50px;'>
    <p style='color: #4A5568; font-size: 12px; font-weight: 600;'>⚡ V20.0 LUXURY EDITION • INSTITUTIONAL ENGINE</p>
</div>
""", unsafe_allow_html=True)
