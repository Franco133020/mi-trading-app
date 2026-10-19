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

# Estilos CSS estilo TradingView Dark
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    .status-long { color: #26a69a; font-weight: bold; font-size: 18px; }
    .status-short { color: #ef5350; font-weight: bold; font-size: 18px; }
    .status-wait { color: #888888; font-weight: bold; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Sistema Scoring + Hyper Markoni + Oracle Oscillator")

# Sidebar - Selección
st.sidebar.header("⚙️ Configuración del Sistema")

ticker_dict = {
    "Grupo Financiero Galicia (GGAL)": {"tv": "BCBA:GGAL", "yf": "GGAL.BA", "adr": "GGAL"},
    "YPF S.A. (YPFD)": {"tv": "BCBA:YPFD", "yf": "YPFD.BA", "adr": "YPF"},
    "Pampa Energía (PAMP)": {"tv": "BCBA:PAMP", "yf": "PAMP.BA", "adr": "PAM"},
    "MercadoLibre (MELI)": {"tv": "BCBA:MELI", "yf": "MELI.BA", "adr": "MELI"},
    "Apple Inc. (AAPL)": {"tv": "NASDAQ:AAPL", "yf": "AAPL", "adr": "AAPL"},
    "NVIDIA Corp. (NVDA)": {"tv": "NASDAQ:NVDA", "yf": "NVDA", "adr": "NVDA"},
    "Bitcoin / USDT": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD", "adr": "BTC-USD"}
}

activo_sel = st.sidebar.selectbox("Seleccionar Activo:", list(ticker_dict.keys()))
tv_symbol = ticker_dict[activo_sel]["tv"]
yf_symbol = ticker_dict[activo_sel]["yf"]
adr_symbol = ticker_dict[activo_sel]["adr"]

# Ticker manual
ticker_custom = st.sidebar.text_input("O Ticker Manual (TradingView):", value="")
if ticker_custom.strip():
    tv_symbol = ticker_custom.strip().upper()
    yf_symbol = tv_symbol.split(":")[-1] + ".BA" if "BCBA" in tv_symbol else tv_symbol.split(":")[-1]
    adr_symbol = tv_symbol.split(":")[-1]

# CÁLCULOS COMPLETOS DEL PINE SCRIPT EN PYTHON
@st.cache_data(ttl=300)
def calcular_matriz_completa(symbol_yf):
    try:
        df = yf.download(symbol_yf, period="1y", interval="1d", progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        close, high, low, open_p, volume = df['Close'], df['High'], df['Low'], df['Open'], df['Volume']
        
        # Medias Móviles
        ma1 = close.ewm(span=8, adjust=False).mean()
        ma2 = close.ewm(span=21, adjust=False).mean()
        ma3 = close.rolling(window=50).mean()
        ma4 = close.ewm(span=100, adjust=False).mean()
        ma5 = close.ewm(span=200, adjust=False).mean()
        
        # Dashboard Variables (% vs MMs)
        asl21 = close.ewm(span=21, adjust=False).mean()
        sma30 = close.rolling(window=30).mean()
        ema150 = close.ewm(span=150, adjust=False).mean()
        ema200 = close.ewm(span=200, adjust=False).mean()
        
        var_asl21 = ((close - asl21) / asl21) * 100
        var_sma30 = ((close - sma30) / sma30) * 100
        var_ema150 = ((close - ema150) / ema150) * 100
        var_ema200 = ((close - ema200) / ema200) * 100
        
        # Desviación Típica (2σ)
        std20 = close.rolling(window=20).std()
        sigma_2 = (2 * std20 / close) * 100
        
        # RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # ATR (14)
        tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        # ADX (14)
        up = high.diff()
        down = -low.diff()
        plus_dm = np.where((up > down) & (up > 0), up, 0)
        minus_dm = np.where((down > up) & (down > 0), down, 0)
        atr_adx = tr.rolling(14).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / atr_adx)
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / atr_adx)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(14).mean()
        
        # Bandas de Bollinger
        bb_basis = close.rolling(window=20).mean()
        bb_dev = 2.0 * std20
        bb_upper = bb_basis + bb_dev
        bb_lower = bb_basis - bb_dev
        
        # MACD (8, 21, 14)
        macd_line = close.ewm(span=8, adjust=False).mean() - close.ewm(span=21, adjust=False).mean()
        signal_line = macd_line.ewm(span=14, adjust=False).mean()
        
        # Oracle Oscillator
        hlc3 = (high + low + close) / 3
        esa = hlc3.ewm(span=10, adjust=False).mean()
        d = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * d)
        ora_wt1 = ci.ewm(span=21, adjust=False).mean()
        ora_wt2 = ora_wt1.rolling(window=4).mean()
        
        # Detección de Patrón de Vela
        cuerpo = (close - open_p).abs()
        mecha_sup = high - np.maximum(close, open_p)
        mecha_inf = np.minimum(close, open_p) - low
        
        patron_nombre = "Sin patrón"
        patron_pts = 0
        
        if (close.iloc[-2] < open_p.iloc[-2]) and (close.iloc[-1] > open_p.iloc[-1]) and (close.iloc[-1] >= open_p.iloc[-2]):
            patron_nombre = "Envolvente Alcista"
            patron_pts = 10
        elif (close.iloc[-2] > open_p.iloc[-2]) and (close.iloc[-1] < open_p.iloc[-1]) and (close.iloc[-1] <= open_p.iloc[-2]):
            patron_nombre = "Envolvente Bajista"
            patron_pts = -10
        elif mecha_inf.iloc[-1] > (cuerpo.iloc[-1] * 2) and mecha_sup.iloc[-1] < cuerpo.iloc[-1]:
            patron_nombre = "Martillo"
            patron_pts = 5
            
        # Valores Actuales
        c_last = float(close.iloc[-1])
        ma1_l, ma2_l, ma3_l, ma4_l, ma5_l = float(ma1.iloc[-1]), float(ma2.iloc[-1]), float(ma3.iloc[-1]), float(ma4.iloc[-1]), float(ma5.iloc[-1])
        rsi_l, adx_l = float(rsi.iloc[-1]), float(adx.iloc[-1])
        wt1_l, wt2_l = float(ora_wt1.iloc[-1]), float(ora_wt2.iloc[-1])
        macd_l, sig_l = float(macd_line.iloc[-1]), float(signal_line.iloc[-1])
        bbu_l, bbl_l, bbm_l = float(bb_upper.iloc[-1]), float(bb_lower.iloc[-1]), float(bb_basis.iloc[-1])
        atr_l = float(atr.iloc[-1])
        
        # Matriz de Scoring (0 a 100)
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
        
        # Filtros y Señal
        is_trending = adx_l >= 20
        if score >= 65 and is_trending:
            signal = "LONG (COMPRA)"
            sl = c_last - (atr_l * 2.0)
            tp = c_last + ((c_last - sl) * 2.0)
        elif score <= 35 and is_trending:
            signal = "SHORT (VENTA)"
            sl = c_last + (atr_l * 2.0)
            tp = c_last - ((sl - c_last) * 2.0)
        else:
            signal = "ESPERA / NEUTRO"
            sl, tp = None, None
            
        return {
            "precio": c_last, "score": score, "signal": signal,
            "var_asl21": float(var_asl21.iloc[-1]), "var_sma30": float(var_sma30.iloc[-1]),
            "var_ema150": float(var_ema150.iloc[-1]), "var_ema200": float(var_ema200.iloc[-1]),
            "rsi": rsi_l, "sigma_2": float(sigma_2.iloc[-1]), "adx": adx_l,
            "wt1": wt1_l, "wt2": wt2_l, "patron": patron_nombre, "patron_pts": patron_pts,
            "ma1": ma1_l, "ma2": ma2_l, "ma3": ma3_l, "ma4": ma4_l, "ma5": ma5_l,
            "macd": macd_l, "signal_macd": sig_l, "bbu": bbu_l, "bbl": bbl_l,
            "sl": sl, "tp": tp
        }
    except Exception:
        return None

# Dólar CCL Ref.
@st.cache_data(ttl=300)
def obtener_ccl():
    try:
        gba = yf.Ticker("GGAL.BA").history(period="1d")['Close'].iloc[-1]
        gadr = yf.Ticker("GGAL").history(period="1d")['Close'].iloc[-1]
        return float((gba / gadr) * 10.0)
    except:
        return None

res = calcular_matriz_completa(yf_symbol)
ccl_val = obtener_ccl()

# INTERFAZ DIBUJADA

# 1. DASHBOARD SUPERIOR (Como el panel de tu script)
st.subheader("📋 Dashboard Técnico Superior")
if res:
    d1, d2, d3, d4, d5, d6, d7, d8 = st.columns(8)
    d1.metric("ASL21", f"{res['var_asl21']:.2f}%")
    d2.metric("SMA30", f"{res['var_sma30']:.2f}%")
    d3.metric("EMA150", f"{res['var_ema150']:.2f}%")
    d4.metric("EMA200", f"{res['var_ema200']:.2f}%")
    d5.metric("RSI", f"{res['rsi']:.1f}")
    d6.metric("2σ Vol", f"{res['sigma_2']:.2f}%")
    d7.metric("ADX", f"{res['adx']:.1f}")
    d8.metric("CCL Ref", f"${ccl_val:.1f}" if ccl_val else "N/A")

st.markdown("---")

# 2. GRÁFICO TRADINGVIEW
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart" style="height:550px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true,
      "symbol": "{tv_symbol}",
      "interval": "D",
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
        "MASimple@tv-basicstudies",
        "STD;Supertrend"
      ]
    }});
  </script>
</div>
"""
components.html(tradingview_html, height=570)

st.markdown("---")

# 3. TABLA MATRICIAL DINÁMICA (Réplica exacta de la tabla Pine Script)
st.subheader("📑 Matriz Integral de Decisiones & Scoring")

if res:
    matriz_data = {
        "MÉTRICA": [
            "Tendencia Precio vs MM",
            "Filtro de Régimen ADX",
            "Oracle Oscillator (WT1)",
            "Patrón de Vela Detectado",
            "Score Bot (0 - 100)",
            "Bandas de Bollinger",
            "Gestión Riesgo (SL / TP ATR)"
        ],
        "VALOR / ESTADO": [
            f"MM8: {'ALCISTA' if res['precio'] > res['ma1'] else 'BAJISTA'} | MM200: {'ALCISTA' if res['precio'] > res['ma5'] else 'BAJISTA'}",
            f"ADX: {res['adx']:.1f} ({'TENDENCIA' if res['adx'] >= 20 else 'RANGO LATERAL'})",
            f"WT1: {res['wt1']:.2f} ({'COMPRA' if res['wt1'] > res['wt2'] else 'VENTA'})",
            f"{res['patron']} ({res['patron_pts']} Pts)",
            f"{res['score']} / 100",
            f"BB SUP: ${res['bbu']:.2f} | BB INF: ${res['bbl']:.2f}",
            f"SEÑAL: {res['signal']} | SL: ${res['sl']:.2f} | TP: ${res['tp']:.2f}" if res['sl'] else f"SEÑAL: {res['signal']}"
        ]
    }
    df_matriz = pd.DataFrame(matriz_data)
    st.table(df_matriz)
