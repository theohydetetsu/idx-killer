<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Engine - Ultimate v18</title>
    <style>
        /* TEMA GELAP (DARK MODE) PREMIUM */
        :root {
            --bg-main: #0B0E11;
            --bg-card: #15191D;
            --text-main: #FFFFFF;
            --text-muted: #8E9BAE;
            --green: #0ECB81;
            --red: #F6465D;
            --gold: #F3BA2F;
            --border: #2B3139;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 16px;
            display: flex;
            justify-content: center;
        }

        .app-container {
            width: 100%;
            max-width: 400px; /* Standar ukuran layar HP */
        }

        /* 1. HEADER LOGO SECTION */
        .header-section {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px dashed var(--border);
        }
        .emiten-logo {
            width: 45px;
            height: 45px;
            background-color: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            overflow: hidden;
        }
        .emiten-logo img {
            width: 100%;
            object-fit: cover;
        }
        .emiten-info h2 {
            margin: 0;
            font-size: 18px;
            letter-spacing: 1px;
        }
        .emiten-info p {
            margin: 2px 0 0 0;
            font-size: 13px;
            color: var(--text-muted);
        }

        /* 2. CARD STYLE UMUM */
        .card {
            background-color: var(--bg-card);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid var(--border);
        }
        .card-title {
            font-size: 12px;
            color: var(--text-muted);
            letter-spacing: 1px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            text-transform: uppercase;
        }

        /* 3. ENTRY & STOP LOSS */
        .entry-sl-container {
            display: flex;
            justify-content: space-between;
            text-align: center;
            margin-top: 10px;
        }
        .entry-box, .sl-box { width: 48%; }
        .label {
            font-size: 10px;
            color: var(--text-muted);
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .value {
            font-size: 24px;
            font-weight: bold;
            margin-top: 5px;
        }
        .value.entry { color: var(--text-main); }
        .value.sl { color: var(--red); }
        .divider {
            width: 1px;
            background-color: var(--border);
            height: 40px;
            margin-top: 10px;
        }

        /* 4. KEPUTUSAN STRATEGI & AI CONCLUSION */
        .btn-buy {
            background-color: rgba(14, 203, 129, 0.1);
            color: var(--green);
            border: 1px solid var(--green);
            width: 100%;
            padding: 15px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 12px;
            text-transform: uppercase;
            box-sizing: border-box;
        }
        .setup-status {
            font-size: 12px;
            color: var(--text-main);
            margin-bottom: 15px;
        }
        .ai-conclusion-box {
            background-color: rgba(255, 255, 255, 0.03);
            border-left: 3px solid var(--gold);
            padding: 12px;
            border-radius: 0 8px 8px 0;
            font-size: 13px;
            line-height: 1.5;
            color: #d1d5db;
        }
        .ai-title {
            color: var(--gold);
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 12px;
        }

        /* 5. FIBONACCI SECTION */
        .fibo-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
        }
        .fibo-row:last-child { border-bottom: none; }
        .fibo-row.highlight { color: var(--gold); font-weight: bold; }

        /* 6. VWAP SECTION */
        .vwap-value {
            font-size: 28px;
            font-weight: bold;
            color: var(--green);
            text-align: center;
            margin: 10px 0;
        }
        .vwap-gap {
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 15px;
        }
        .btn-bullish {
            background-color: rgba(14, 203, 129, 0.15);
            color: var(--green);
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            display: inline-block;
            border: 1px solid var(--green);
        }
    </style>
</head>
<body>

<div class="app-container">

    <!-- HEADER LOGO (FITUR BARU) -->
    <div class="header-section">
        <div class="emiten-logo">
            <!-- Ganti URL ini dengan logo dinamis dari sistem Anda -->
            <img id="logoEmiten" src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Logo_BRI.png/1200px-Logo_BRI.png" alt="Logo">
        </div>
        <div class="emiten-info">
            <h2 id="kodeEmiten">BBRI</h2>
            <p id="namaEmiten">Bank Rakyat Indonesia Tbk.</p>
        </div>
    </div>

    <!-- ENTRY & STOP LOSS -->
    <div class="card">
        <div class="card-title">🎯 ENTRY & 🚨 STOP LOSS</div>
        <div class="entry-sl-container">
            <div class="entry-box">
                <div class="label">Entry Area</div>
                <div class="value entry" id="valEntry">379</div>
            </div>
            <div class="divider"></div>
            <div class="sl-box">
                <div class="label">Stop Loss</div>
                <div class="value sl" id="valSL">374</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 15px; font-size: 10px; color: var(--text-muted);">
            Auto Chandelier / Tolerance
        </div>
    </div>

    <!-- KEPUTUSAN STRATEGI + AI CONCLUSION (FITUR BARU) -->
    <div class="card">
        <div class="card-title">🛡️ KEPUTUSAN STRATEGI</div>
        
        <div class="btn-buy" id="btnSignal">BUY / ACCUMULATE</div>
        
        <div class="setup-status">
            Status Setup: 🎯 <b style="color: var(--gold);">SETUP JACKPOT</b>
        </div>

        <div class="ai-conclusion-box">
            <div class="ai-title">🤖 AI Executive Conclusion</div>
            <div id="aiText">
                Memuat analisis AI...
            </div>
        </div>
    </div>

    <!-- ENGINE SIGNAL -->
    <div class="card" style="text-align: center;">
        <div class="card-title" style="justify-content: center;">⚡ ENGINE SIGNAL</div>
        <div style="font-size: 24px; margin: 10px 0;">🐳</div>
        <div style="font-size: 12px; color: var(--text-muted);">AI Validation Active</div>
    </div>

    <!-- FIBONACCI RETRACEMENT -->
    <div class="card">
        <div class="card-title">📐 FIBONACCI RETRACEMENT (120D)</div>
        <div class="fibo-row">
            <span>100% (High)</span> <span>466</span>
        </div>
        <div class="fibo-row highlight">
            <span>61.8% (Golden Pocket)</span> <span>374</span>
        </div>
        <div class="fibo-row">
            <span>50.0% (Equilibrium)</span> <span>392</span>
        </div>
        <div class="fibo-row">
            <span>38.2%</span> <span>409</span>
        </div>
        <div class="fibo-row">
            <span>0% (Low)</span> <span>317</span>
        </div>
    </div>

    <!-- VWAP -->
    <div class="card" style="text-align: center;">
        <div class="card-title" style="justify-content: center;">⚖️ VWAP (20D)</div>
        <div class="vwap-value">381</div>
        <div class="vwap-gap">Gap to VWAP: <span style="color: var(--green);">+1.31%</span></div>
        <div>
            <span class="btn-bullish">BULLISH (P > VWAP)</span>
        </div>
    </div>

</div>

<!-- SCRIPT LOGIC (OTOMATISASI DATA) -->
<script>
    // 1. Database Dummy (Bisa ditarik dari API/Backend Anda)
    const tradingData = {
        ticker: "BBRI",
        nama: "Bank Rakyat Indonesia Tbk.",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Logo_BRI.png/1200px-Logo_BRI.png",
        entry: 379,
        sl: 374,
        signal: "BUY / ACCUMULATE",
        // Parameter untuk AI Generator
        paramTeknikal: "Support Golden Pocket 61.8%",
        paramBandarmologi: "Akumulasi masif dari Whale",
        paramVWAP: "Bullish (Harga di atas VWAP)",
        paramFundamental: "Kinerja fundamental stabil"
    };

    // 2. Fungsi perakit teks AI
    function generateAIConclusion(data) {
        return `<b>Sinyal Beli Kuat!</b> Terdeteksi ${data.paramBandarmologi} tepat di area krusial ${data.paramTeknikal}. Momentum saat ini ${data.paramVWAP} dan didukung ${data.paramFundamental}. <br><br><i>Insight: Eksekusi di ${data.entry} memberikan potensi pantulan (Jackpot) dengan risiko Cut Loss sangat rendah.</i>`;
    }

    // 3. Render Data ke Layar saat aplikasi dibuka
    window.onload = function() {
        document.getElementById("kodeEmiten").innerText = tradingData.ticker;
        document.getElementById("namaEmiten").innerText = tradingData.nama;
        document.getElementById("logoEmiten").src = tradingData.logo;
        
        document.getElementById("valEntry").innerText = tradingData.entry;
        document.getElementById("valSL").innerText = tradingData.sl;
        document.getElementById("btnSignal").innerText = tradingData.signal;
        
        document.getElementById("aiText").innerHTML = generateAIConclusion(tradingData);
    };
</script>

</body>
</html>
