import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Sistema Scoring + Markoni + Oracle",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alto contraste tipo TradingView
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    
    /* Estilos para la tabla matricial */
    .matriz-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 13px;
        color: white;
        margin-top: 15px;
    }
    .matriz-table th, .matriz-table td {
        border: 1px solid #2a2e39;
        padding: 8px;
        text-align: center;
    }
    .matriz-header { background-color: #1e222d; font-weight: bold; }
    .bg-dark { background-color: #2a2e39; }
    .bg-green { background-color: #26a69a; color: white; }
    .bg-red { background-color: #ef5350; color: white; }
    .bg-orange { background-color: #ff9800; color: white; }
    .bg-navy { background-color: #1a237e; color: white; }
    .bg-teal { background-color: #00796b; color: white; }
    .bg-purple { background-color: #4a148c; color: white; }
    .bg-gold { background-color: #f57f17; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Sistema Scoring + Hyper Markoni + Oracle Oscillator")

# Sidebar - Selección de Activo
st.sidebar.header("⚙️ Configuración del Activo")

ticker_dict = {
    "McDonald's (MCD)": {"tv": "NYSE:MCD", "yf": "MCD"},
    "Grupo Financiero Galicia (GGAL)": {"tv": "BCBA:GGAL", "yf": "GGAL.BA"},
    "YPF S.A. (YPFD)": {"tv": "BCBA:YPFD", "yf": "YPFD.BA"},
    "Apple Inc. (AAPL)": {"tv": "NASDAQ:AAPL", "yf": "AAPL"},
    "NVIDIA Corp. (NVDA)": {"tv": "NASDAQ:NVDA", "yf": "NVDA"},
    "Bitcoin / USDT": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD"}
}

activo_sel = st.sidebar.selectbox("Seleccionar Activo:", list(ticker_dict.keys()))
tv_symbol = ticker_dict[activo_sel]["tv"]
yf_symbol = ticker_dict[activo_sel]["yf"]

ticker_custom = st.sidebar.text_input("O Ticker Manual (TradingView):", value="")
if ticker_custom.strip():
    tv_symbol = ticker_custom.strip().upper()
    yf_symbol = tv_symbol.split(":")[-1] + ".BA" if "BCBA" in tv_symbol else tv_symbol.split(":")[-1]

# CÁLCULOS MATEMÁTICOS DE PINE SCRIPT
@st.cache_data(ttl=300)
def calcular_matriz_pine(symbol_yf):
    try:
        df = yf.download(symbol_yf, period="1y", interval="1d", progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        close, high, low, open_p, volume = df['Close'], df['High'], df['Low'], df['Open'], df['Volume']
        
        # MMs
        ma1 = close.ewm(span=8, adjust=False).mean()
        ma2 = close.ewm(span=21, adjust=False).mean()
        ma3 = close.rolling(window=50).mean()
        ma4 = close.ewm(span=100, adjust=False).mean()
        ma5 = close.ewm(span=200, adjust=False).mean()
        
        # Dashboard Variables
        asl21 = close.ewm(span=21, adjust=False).mean()
        sma30 = close.rolling(window=30).mean()
        ema150 = close.ewm(span=150, adjust=False).mean()
        ema200 = close.ewm(span=200, adjust=False).mean()
        
        # RSI y ATR
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        # ADX
        up, down = high.diff(), -low.diff()
        plus_dm = np.where((up > down) & (up > 0), up, 0)
        minus_dm = np.where((down > up) & (down > 0), down, 0)
        atr_14 = tr.rolling(14).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / atr_14)
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / atr_14)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(14).mean()
        
        # BB y MACD
        bb_basis = close.rolling(window=20).mean()
        bb_dev = 2.0 * close.rolling(window=20).std()
        bb_upper = bb_basis + bb_dev
        bb_lower = bb_basis - bb_dev
        
        macd_line = close.ewm(span=8, adjust=False).mean() - close.ewm(span=21, adjust=False).mean()
        signal_line = macd_line.ewm(span=14, adjust=False).mean()
        
        # Oracle Oscillator
        hlc3 = (high + low + close) / 3
        esa = hlc3.ewm(span=10, adjust=False).mean()
        d = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * d)
        ora_wt1 = ci.ewm(span=21, adjust=False).mean()
        ora_wt2 = ora_wt1.rolling(window=4).mean()
        
        # Patrón de Vela
        patron_nombre, patron_pts, desc_patron = "Sin patrón", 0, "-"
        if (close.iloc[-2] < open_p.iloc[-2]) and (close.iloc[-1] > open_p.iloc[-1]) and (close.iloc[-1] >= open_p.iloc[-2]):
            patron_nombre, patron_pts, desc_patron = "Envolvente Alc", 10, "Absorción compradora"
        elif (close.iloc[-2] > open_p.iloc[-2]) and (close.iloc[-1] < open_p.iloc[-1]) and (close.iloc[-1] <= open_p.iloc[-2]):
            patron_nombre, patron_pts, desc_patron = "Envolvente Baj", -10, "Absorción vendedora"
            
        c_last = float(close.iloc[-1])
        ma1_l, ma2_l, ma3_l, ma4_l, ma5_l = float(ma1.iloc[-1]), float(ma2.iloc[-1]), float(ma3.iloc[-1]), float(ma4.iloc[-1]), float(ma5.iloc[-1])
        rsi_l, adx_l, atr_l = float(rsi.iloc[-1]), float(adx.iloc[-1]), float(atr.iloc[-1])
        wt1_l, wt2_l = float(ora_wt1.iloc[-1]), float(ora_wt2.iloc[-1])
        macd_l, sig_l = float(macd_line.iloc[-1]), float(signal_line.iloc[-1])
        bbu_l, bbl_l, bbm_l = float(bb_upper.iloc[-1]), float(bb_lower.iloc[-1]), float(bb_basis.iloc[-1])
        
        # Score Bot
        score = 0
        if c_last > ma5_l: score += 10
        if c_last > ma3_l: score += 5
        if ma1_l > ma2_l: score += 5
        if c_last > ma1_l: score += 5
        if rsi_l >= 50 and rsi_l <= 70: score += 10
        if macd_l > sig_l: score += 5
        if c_last > bbm_l: score += 5
        if wt1_l > wt2_l: score += 10
        if wt1_l > 0: score += 5
        if wt1_l < 50: score += 5
        score += patron_pts
        
        is_trending = adx_l >= 20
        if score >= 65 and is_trending:
            signal = "LONG"
            sl = c_last - (atr_l * 2.0)
            tp = c_last + ((c_last - sl) * 2.0)
        elif score <= 35 and is_trending:
            signal = "SHORT"
            sl = c_last + (atr_l * 2.0)
            tp = c_last - ((sl - c_last) * 2.0)
        else:
            signal = "ESPERA"
            sl, tp = None, None
            
        return {
            "precio": c_last, "score": score, "signal": signal,
            "rsi": rsi_l, "adx": adx_l, "wt1": wt1_l, "wt2": wt2_l,
            "patron": patron_nombre, "desc_patron": desc_patron, "patron_pts": patron_pts,
            "ma1": ma1_l, "ma2": ma2_l, "ma3": ma3_l, "ma4": ma4_l, "ma5": ma5_l,
            "macd": macd_l, "sig": sig_l, "bbu": bbu_l, "bbl": bbl_l, "sl": sl, "tp": tp,
            "is_trending": is_trending
        }
    except Exception:
        return None

res = calcular_matriz_pine(yf_symbol)

# RENDER DEL GRÁFICO
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart" style="height:550px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true,
      "symbol": "{tv_symbol}",
      "interval": "60",
      "timezone": "America/Argentina/Jujuy",
      "theme": "dark",
      "style": "1",
      "locale": "es",
      "toolbar_bg": "#1e222d",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart",
      "hide_side_toolbar": false,
      "studies": [
        "RSI@tv-basicstudies",
        "MACD@tv-basicstudies",
        "MASimple@tv-basicstudies"
      ]
    }});
  </script>
</div>
"""
components.html(tradingview_html, height=560)

st.markdown("---")

# RENDER DE LA TABLA MATRICIAL DE 6 COLUMNAS (Réplica exacta de tu imagen)
st.subheader("📑 Tabla Matricial del Sistema de Trading")

if res:
    matriz_html = f"""
    <table class="matriz-table">
        <tr class="matriz-header">
            <td>MÉTRICA</td>
            <td>MM 8</td>
            <td>MM 21</td>
            <td>MM 50</td>
            <td>MM 100</td>
            <td>MM 200</td>
        </tr>
        <tr>
            <td class="bg-dark">Tendencia</td>
            <td class="{'bg-green' if res['precio'] > res['ma1'] else 'bg-red'}">{'ALCISTA' if res['precio'] > res['ma1'] else 'BAJISTA'}</td>
            <td class="{'bg-green' if res['precio'] > res['ma2'] else 'bg-red'}">{'ALCISTA' if res['precio'] > res['ma2'] else 'BAJISTA'}</td>
            <td class="{'bg-green' if res['precio'] > res['ma3'] else 'bg-red'}">{'ALCISTA' if res['precio'] > res['ma3'] else 'BAJISTA'}</td>
            <td class="{'bg-green' if res['precio'] > res['ma4'] else 'bg-red'}">{'ALCISTA' if res['precio'] > res['ma4'] else 'BAJISTA'}</td>
            <td class="{'bg-green' if res['precio'] > res['ma5'] else 'bg-red'}">{'ALCISTA' if res['precio'] > res['ma5'] else 'BAJISTA'}</td>
        </tr>
        <tr>
            <td class="bg-navy">FILTROS OPT.</td>
            <td class="{'bg-green' if res['is_trending'] else 'bg-red'}">ADX ({res['adx']:.1f})</td>
            <td class="bg-dark">RÉGIMEN</td>
            <td class="{'bg-teal' if res['is_trending'] else 'bg-orange'}">{'TENDENCIA' if res['is_trending'] else 'RANGO LATERAL'}</td>
            <td class="bg-dark">CONF. MTF (W)</td>
            <td class="{'bg-green' if res['precio'] > res['ma2'] else 'bg-red'}">{'ALCISTA' if res['precio'] > res['ma2'] else 'BAJISTA'}</td>
        </tr>
        <tr>
            <td class="bg-orange">ORACLE</td>
            <td class="bg-dark">Estándar</td>
            <td class="bg-dark">VALOR WT1</td>
            <td class="bg-dark">{res['wt1']:.2f}</td>
            <td class="bg-dark">ESTADO ORACLE</td>
            <td class="{'bg-green' if res['wt1'] > res['wt2'] else 'bg-red'}">{'COMPRA' if res['wt1'] > res['wt2'] else 'VENTA'}</td>
        </tr>
        <tr>
            <td class="bg-purple">PATRÓN VELA</td>
            <td class="bg-dark">{res['patron']}</td>
            <td class="bg-dark">RESEÑA TÉCNICA</td>
            <td class="bg-dark">{res['desc_patron']}</td>
            <td class="bg-dark">PTS PATRÓN</td>
            <td class="bg-dark">{res['patron_pts']} Pts</td>
        </tr>
        <tr>
            <td class="bg-navy">SCORE BOT</td>
            <td class="{'bg-green' if res['score']>=65 else ('bg-red' if res['score']<=35 else 'bg-orange')}">{res['score']} / 100</td>
            <td class="bg-dark">ESTADO RSI</td>
            <td class="bg-dark">{'SOBRECOMPRA' if res['rsi']>70 else ('SOBREVENTA' if res['rsi']<30 else 'NEUTRO')}</td>
            <td class="bg-dark">VALOR RSI</td>
            <td class="bg-dark">{res['rsi']:.1f}</td>
        </tr>
        <tr>
            <td class="bg-gold">SEÑAL BOT</td>
            <td class="{'bg-green' if res['signal']=='LONG' else ('bg-red' if res['signal']=='SHORT' else 'bg-dark')}">{res['signal']}</td>
            <td class="bg-dark">PRECIO ENTRADA</td>
            <td class="bg-dark">${res['precio']:.2f}</td>
            <td class="bg-dark">RATIO R:B REAL</td>
            <td class="bg-dark">1 : 2.0</td>
        </tr>
        <tr>
            <td class="bg-purple">GESTIÓN RIESGO</td>
            <td class="bg-red">STOP LOSS (ATR)</td>
            <td class="bg-red">${res['sl']:.2f} if res['sl'] else 'N/A'</td>
            <td class="bg-green">TAKE PROFIT</td>
            <td class="bg-green">${res['tp']:.2f} if res['tp'] else 'N/A'</td>
            <td class="bg-dark">RIESGO: 2.5%</td>
        </tr>
    </table>
    """
    st.markdown(matriz_html, unsafe_allow_html=True)
