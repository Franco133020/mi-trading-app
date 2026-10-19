import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de la página Streamlit
st.set_page_config(
    page_title="Sistema Scoring + Markoni + Oracle",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Modo Oscuro Profesional)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    .status-long { color: #26a69a; font-weight: bold; font-size: 20px; }
    .status-short { color: #ef5350; font-weight: bold; font-size: 20px; }
    .status-wait { color: #888888; font-weight: bold; font-size: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Sistema Scoring + Hyper Markoni + Oracle Oscillator")

# Sidebar - Panel de Control
st.sidebar.header("⚙️ Configuración del Sistema")

# Selección de Ticker y mapeo
ticker_dict = {
    "Grupo Financiero Galicia (GGAL)": {"tv": "BCBA:GGAL", "yf": "GGAL.BA"},
    "YPF S.A. (YPFD)": {"tv": "BCBA:YPFD", "yf": "YPFD.BA"},
    "Pampa Energía (PAMP)": {"tv": "BCBA:PAMP", "yf": "PAMP.BA"},
    "MercadoLibre (MELI)": {"tv": "BCBA:MELI", "yf": "MELI.BA"},
    "Apple Inc. (AAPL)": {"tv": "NASDAQ:AAPL", "yf": "AAPL"},
    "NVIDIA Corp. (NVDA)": {"tv": "NASDAQ:NVDA", "yf": "NVDA"},
    "Bitcoin / USDT": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD"}
}

activo_sel = st.sidebar.selectbox("Seleccionar Activo:", list(ticker_dict.keys()))
tv_symbol = ticker_dict[activo_sel]["tv"]
yf_symbol = ticker_dict[activo_sel]["yf"]

# Opción de Ticker Manual
ticker_custom = st.sidebar.text_input("O Ticker Manual (TradingView):", value="")
if ticker_custom.strip():
    tv_symbol = ticker_custom.strip().upper()
    yf_symbol = tv_symbol.split(":")[-1] + ".BA" if "BCBA" in tv_symbol else tv_symbol.split(":")[-1]

# Temporalidad para el Gráfico
intervalos_tv = {
    "Diario": "D",
    "1 Hora": "60",
    "15 Minutos": "15",
    "Semanal": "W"
}
temp_sel = st.sidebar.selectbox("Temporalidad Gráfico:", list(intervalos_tv.keys()), index=0)

# ==========================================
# CÁLCULOS MATEMÁTICOS DE PINE SCRIPT EN PYTHON
# ==========================================

@st.cache_data(ttl=300)
def calcular_sistema_scoring(symbol_yf):
    try:
        df = yf.download(symbol_yf, period="1y", interval="1d", progress=False)
        if df.empty:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # 1. Medias Móviles (EMA)
        ma1 = close.ewm(span=8, adjust=False).mean()
        ma2 = close.ewm(span=21, adjust=False).mean()
        ma3 = close.ewm(span=50, adjust=False).mean()
        ma5 = close.ewm(span=200, adjust=False).mean()
        
        # 2. RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 3. MACD (8, 21, 14)
        ema_fast = close.ewm(span=8, adjust=False).mean()
        ema_slow = close.ewm(span=21, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=14, adjust=False).mean()
        
        # 4. Bandas de Bollinger (20, 2)
        bb_basis = close.rolling(window=20).mean()
        
        # 5. ATR (14)
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        # 6. Oracle Oscillator
        hlc3 = (high + low + close) / 3
        esa = hlc3.ewm(span=10, adjust=False).mean()
        d = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * d)
        ora_wt1 = ci.ewm(span=21, adjust=False).mean()
        ora_wt2 = ora_wt1.rolling(window=4).mean()
        
        # Valores de la última vela
        c_last = float(close.iloc[-1])
        ma1_last, ma2_last, ma3_last, ma5_last = float(ma1.iloc[-1]), float(ma2.iloc[-1]), float(ma3.iloc[-1]), float(ma5.iloc[-1])
        rsi_last = float(rsi.iloc[-1])
        macd_last, signal_last = float(macd_line.iloc[-1]), float(signal_line.iloc[-1])
        bb_basis_l = float(bb_basis.iloc[-1])
        atr_last = float(atr.iloc[-1])
        wt1_last, wt2_last = float(ora_wt1.iloc[-1]), float(ora_wt2.iloc[-1])
        
        # 7. MATRIZ DE SCORING (0 a 100)
        score = 0
        if c_last > ma5_last: score += 10
        if c_last > ma3_last: score += 5
        if ma1_last > ma2_last: score += 5
        if c_last > ma1_last: score += 5
        if rsi_last >= 50 and rsi_last <= 70: score += 10
        if macd_last > signal_last: score += 5
        if c_last > bb_basis_l: score += 5
        if wt1_last > wt2_last: score += 10
        if wt1_last > 0: score += 5
        if wt1_last < 50: score += 5
        
        # Gestión de Señal y SL/TP por ATR
        if score >= 65:
            trade_signal = "LONG (COMPRA)"
            sl_sugerido = c_last - (atr_last * 2.0)
            tp_sugerido = c_last + ((c_last - sl_sugerido) * 2.0)
        elif score <= 35:
            trade_signal = "SHORT (VENTA)"
            sl_sugerido = c_last + (atr_last * 2.0)
            tp_sugerido = c_last - ((sl_sugerido - c_last) * 2.0)
        else:
            trade_signal = "ESPERA / NEUTRO"
            sl_sugerido = None
            tp_sugerido = None
            
        return {
            "precio": c_last,
            "score": score,
            "signal": trade_signal,
            "rsi": rsi_last,
            "wt1": wt1_last,
            "sl": sl_sugerido,
            "tp": tp_sugerido
        }
    except Exception:
        return None

# Mapeo Dólar CCL (GGAL BA vs GGAL ADR)
@st.cache_data(ttl=300)
def calcular_dolar_ccl():
    try:
        ggal_ba = yf.Ticker("GGAL.BA").history(period="1d")['Close'].iloc[-1]
        ggal_adr = yf.Ticker("GGAL").history(period="1d")['Close'].iloc[-1]
        ccl = (ggal_ba / ggal_adr) * 10.0
        return float(ccl)
    except Exception:
        return None

# Ejecutar Cálculos
res = calcular_sistema_scoring(yf_symbol)
ccl_val = calcular_dolar_ccl()

# ==========================================
# INTERFAZ GRÁFICA EN STREAMLIT
# ==========================================

col1, col2, col3, col4, col5 = st.columns(5)

if res:
    with col1:
        st.metric("Precio Actual", f"${res['precio']:.2f}")
    with col2:
        st.metric("Score Bot", f"{res['score']} / 100")
    with col3:
        st.metric("RSI (14)", f"{res['rsi']:.1f}")
    with col4:
        st.metric("Oracle WT1", f"{res['wt1']:.1f}")
    with col5:
        ccl_txt = f"${ccl_val:.2f}" if ccl_val else "N/A"
        st.metric("Dólar CCL Ref.", ccl_txt)

    st.markdown("---")
    c_sig1, c_sig2, c_sig3 = st.columns([2, 2, 2])
    
    with c_sig1:
        if "LONG" in res['signal']:
            st.markdown(f"**Señal del Bot:** <span class='status-long'>{res['signal']}</span>", unsafe_allow_html=True)
        elif "SHORT" in res['signal']:
            st.markdown(f"**Señal del Bot:** <span class='status-short'>{res['signal']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Señal del Bot:** <span class='status-wait'>{res['signal']}</span>", unsafe_allow_html=True)

    with c_sig2:
        sl_txt = f"${res['sl']:.2f}" if res['sl'] else "N/A"
        st.markdown(f"**Stop Loss (ATR):** `{sl_txt}`")

    with c_sig3:
        tp_txt = f"${res['tp']:.2f}" if res['tp'] else "N/A"
        st.markdown(f"**Take Profit (R:B 1:2):** `{tp_txt}`")

st.markdown("---")

# Renderizado del Gráfico TradingView Completo
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart" style="height:620px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true,
      "symbol": "{tv_symbol}",
      "interval": "{intervalos_tv[temp_sel]}",
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

components.html(tradingview_html, height=640)
