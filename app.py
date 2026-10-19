import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_lightweight_charts import renderLightweightCharts

# Configuración de la página
st.set_page_config(
    page_title="Sistema Scoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alto contraste
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    
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

# Título Principal
st.markdown("""
    <h2 style='text-align: left; color: #ffffff; margin-bottom: 20px;'>
        📊 Sistema Scoring
    </h2>
""", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 1: CONFIGURACIÓN GENERAL DEL ACTIVO
# ==========================================
st.sidebar.header("⚙️ Configuración del Activo")

ticker_dict = {
    "McDonald's (MCD)": "MCD",
    "Grupo Financiero Galicia (GGAL)": "GGAL.BA",
    "YPF S.A. (YPFD)": "YPFD.BA",
    "Apple Inc. (AAPL)": "AAPL",
    "NVIDIA Corp. (NVDA)": "NVDA",
    "Bitcoin / USDT": "BTC-USD"
}

activo_sel = st.sidebar.selectbox("Seleccionar Activo:", list(ticker_dict.keys()))
yf_symbol = ticker_dict[activo_sel]

ticker_custom = st.sidebar.text_input("O Ticker Manual (yfinance):", value="")
if ticker_custom.strip():
    yf_symbol = ticker_custom.strip().upper()

timeframe_map = {
    "1 Minuto": {"yf_interval": "1m", "yf_period": "7d"},
    "5 Minutos": {"yf_interval": "5m", "yf_period": "30d"},
    "15 Minutos": {"yf_interval": "15m", "yf_period": "60d"},
    "30 Minutos": {"yf_interval": "30m", "yf_period": "60d"},
    "1 Hora": {"yf_interval": "1h", "yf_period": "730d"},
    "Diario (1D)": {"yf_interval": "1d", "yf_period": "5y"},
    "Semanal (1W)": {"yf_interval": "1wk", "yf_period": "10y"}
}

tf_sel = st.sidebar.selectbox("Temporalidad del Análisis:", list(timeframe_map.keys()), index=4)
yf_interval = timeframe_map[tf_sel]["yf_interval"]
yf_period = timeframe_map[tf_sel]["yf_period"]

# ==========================================
# SECCIÓN 2: CONTROLES DE INDICADORES (SIDEBAR)
# ==========================================
with st.sidebar.expander("📈 Medias Móviles", expanded=True):
    use_mm1 = st.checkbox("MM1 (8)", value=True)
    len_mm1 = st.number_input("Período MM1", value=8, step=1)
    
    use_mm2 = st.checkbox("MM2 (21)", value=True)
    len_mm2 = st.number_input("Período MM2", value=21, step=1)
    
    use_mm3 = st.checkbox("MM3 (50)", value=True)
    len_mm3 = st.number_input("Período MM3", value=50, step=1)
    
    use_mm4 = st.checkbox("MM4 (100)", value=True)
    len_mm4 = st.number_input("Período MM4", value=100, step=1)
    
    use_mm5 = st.checkbox("MM5 (200)", value=True)
    len_mm5 = st.number_input("Período MM5", value=200, step=1)

with st.sidebar.expander("⚙️ Bandas de Bollinger & SuperTrend", expanded=False):
    use_bb = st.checkbox("Activar Bandas de Bollinger", value=True)
    use_st = st.checkbox("Activar SuperTrend", value=True)
    st_period = st.number_input("Período SuperTrend", value=22, step=1)
    st_mult = st.number_input("Multiplicador SuperTrend", value=3.0, step=0.1)

with st.sidebar.expander("🎯 Filtros y Gestión de Riesgo", expanded=False):
    use_adx_filter = st.checkbox("Filtro ADX", value=True)
    adx_th = st.number_input("Umbral ADX", value=20, step=1)
    rsi_ob_limit = st.number_input("Límite RSI Compra", value=70.0, step=1.0)
    rsi_os_limit = st.number_input("Límite RSI Venta", value=30.0, step=1.0)
    fallback_ratio = st.number_input("Ratio R:B", value=2.0, step=0.1)

# ==========================================
# PROCESAMIENTO DE DATOS E INDICADORES
# ==========================================
@st.cache_data(ttl=60)
def cargar_y_calcular_datos(symbol, interval, period, m1, m2, m3, m4, m5, st_p, st_m):
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if df.empty or len(df) < 30:
        return None
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df.reset_index()
    time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
    
    # FORMATO UNIX TIMESTAMP EN SEGUNDOS PARA LIGHTWEIGHT CHARTS
    df['time'] = (df[time_col].astype('int64') // 10**9)
    
    close, high, low, open_p = df['Close'], df['High'], df['Low'], df['Open']
    
    # Medias Móviles
    df['ma1'] = close.ewm(span=m1, adjust=False).mean()
    df['ma2'] = close.ewm(span=m2, adjust=False).mean()
    df['ma3'] = close.ewm(span=m3, adjust=False).mean()
    df['ma4'] = close.ewm(span=m4, adjust=False).mean()
    df['ma5'] = close.ewm(span=m5, adjust=False).mean()
    
    # Bollinger
    df['bb_basis'] = close.rolling(window=20).mean()
    dev = 2.0 * close.rolling(window=20).std()
    df['bb_upper'] = df['bb_basis'] + dev
    df['bb_lower'] = df['bb_basis'] - dev
    
    # RSI & ATR
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + (gain / loss)))
    
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    df['atr'] = tr.ewm(alpha=1/14, adjust=False).mean()
    
    # ADX
    up, down = high.diff(), -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0), index=df.index)
    tr_smooth = tr.ewm(alpha=1/14, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/14, adjust=False).mean() / tr_smooth)
    minus_di = 100 * (minus_dm.ewm(alpha=1/14, adjust=False).mean() / tr_smooth)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df['adx'] = dx.ewm(alpha=1/14, adjust=False).mean()
    
    # SuperTrend
    hl2 = (high + low) / 2
    st_atr = tr.ewm(alpha=1/st_p, adjust=False).mean()
    up_band = hl2 - (st_m * st_atr)
    dn_band = hl2 + (st_m * st_atr)
    st_dir = np.zeros(len(df))
    st_line = np.zeros(len(df))
    
    for i in range(1, len(df)):
        if close.iloc[i] > dn_band.iloc[i-1]:
            st_dir[i] = -1
        elif close.iloc[i] < up_band.iloc[i-1]:
            st_dir[i] = 1
        else:
            st_dir[i] = st_dir[i-1]
        st_line[i] = up_band.iloc[i] if st_dir[i] == -1 else dn_band.iloc[i]
        
    df['st_line'] = st_line
    df['st_dir'] = st_dir
    
    # Oracle Oscillator
    hlc3 = (high + low + close) / 3
    esa = hlc3.ewm(span=10, adjust=False).mean()
    d = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
    ci = (hlc3 - esa) / (0.015 * d)
    df['ora_wt1'] = ci.ewm(span=21, adjust=False).mean()
    df['ora_wt2'] = df['ora_wt1'].rolling(window=4).mean()
    
    return df

df_data = cargar_y_calcular_datos(
    yf_symbol, yf_interval, yf_period, 
    len_mm1, len_mm2, len_mm3, len_mm4, len_mm5, 
    st_period, st_mult
)

# ==========================================
# CONSTRUCCIÓN DEL GRÁFICO DINÁMICO
# ==========================================
if df_data is not None:
    chart_candles = []
    for _, row in df_data.iterrows():
        chart_candles.append({
            "time": int(row['time']),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close'])
        })
        
    series_list = [{
        "type": "Candlestick",
        "data": chart_candles,
        "options": {
            "upColor": "#26a69a",
            "downColor": "#ef5350",
            "borderVisible": False,
            "wickUpColor": "#26a69a",
            "wickDownColor": "#ef5350"
        }
    }]
    
    def add_line_series(column_name, color_hex, title_name):
        line_data = [{"time": int(row['time']), "value": float(row[column_name])} for _, row in df_data.iterrows() if not np.isnan(row[column_name])]
        series_list.append({
            "type": "Line",
            "data": line_data,
            "options": {"color": color_hex, "lineWidth": 2, "title": title_name}
        })

    if use_mm1: add_line_series('ma1', '#00FFFF', f'MM {len_mm1}')
    if use_mm2: add_line_series('ma2', '#FF9800', f'MM {len_mm2}')
    if use_mm3: add_line_series('ma3', '#FFFF00', f'MM {len_mm3}')
    if use_mm4: add_line_series('ma4', '#0000FF', f'MM {len_mm4}')
    if use_mm5: add_line_series('ma5', '#FF0000', f'MM {len_mm5}')
    
    if use_bb:
        add_line_series('bb_upper', '#2196F3', 'BB Sup')
        add_line_series('bb_basis', '#FF9800', 'BB Mid')
        add_line_series('bb_lower', '#2196F3', 'BB Inf')
        
    if use_st:
        add_line_series('st_line', '#E91E63', 'SuperTrend')

    chart_options = {
        "layout": {
            "backgroundColor": "#0e1117",
            "textColor": "#d1d4dc"
        },
        "grid": {
            "vertLines": {"color": "#1e222d"},
            "horzLines": {"color": "#1e222d"}
        },
        "height": 500
    }
    
    renderLightweightCharts([{"chart": chart_options, "series": series_list}])

st.markdown("---")

# ==========================================
# CÁLCULO Y RENDER DE LA TABLA MATRICIAL
# ==========================================
st.subheader(f"📑 Tabla Matricial del Sistema de Trading ({tf_sel})")

if df_data is not None:
    last = df_data.iloc[-1]
    c_last = float(last['Close'])
    
    score = 0
    if use_mm5 and c_last > last['ma5']: score += 10
    if use_mm3 and c_last > last['ma3']: score += 5
    if use_mm1 and use_mm2 and last['ma1'] > last['ma2']: score += 5
    if use_mm1 and c_last > last['ma1']: score += 5
    if use_st and last['st_dir'] < 0: score += 10
    if last['rsi'] >= 50 and last['rsi'] <= rsi_ob_limit: score += 10
    if c_last > last['bb_basis']: score += 5
    if last['ora_wt1'] > last['ora_wt2']: score += 10
    if last['ora_wt1'] > 0: score += 5
    if last['ora_wt1'] < 40.0: score += 5
    
    is_trending = (not use_adx_filter) or (last['adx'] >= adx_th)
    rsi_ok = (last['rsi'] < rsi_ob_limit)
    
    if score >= 75 and is_trending and rsi_ok:
        signal, sl, tp = "LONG", c_last - (last['atr'] * 2.0), c_last + (last['atr'] * 2.0 * fallback_ratio)
    elif score <= 25 and is_trending:
        signal, sl, tp = "SHORT", c_last + (last['atr'] * 2.0), c_last - (last['atr'] * 2.0 * fallback_ratio)
    else:
        signal, sl, tp = "ESPERA", None, None

    c_ma1 = "bg-green" if c_last > last['ma1'] else "bg-red"
    c_ma2 = "bg-green" if c_last > last['ma2'] else "bg-red"
    c_ma3 = "bg-green" if c_last > last['ma3'] else "bg-red"
    c_ma4 = "bg-green" if c_last > last['ma4'] else "bg-red"
    c_ma5 = "bg-green" if c_last > last['ma5'] else "bg-red"

    c_adx = "bg-green" if is_trending else "bg-red"
    c_reg = "bg-teal" if is_trending else "bg-orange"
    c_ora = "bg-green" if last['ora_wt1'] > last['ora_wt2'] else "bg-red"
    c_score = "bg-green" if score >= 75 else ("bg-red" if score <= 25 else "bg-orange")
    c_sig = "bg-green" if signal == "LONG" else ("bg-red" if signal == "SHORT" else "bg-dark")

    sl_str = f"${sl:.2f}" if sl is not None else "N/A"
    tp_str = f"${tp:.2f}" if tp is not None else "N/A"

    matriz_html = f"""
    <table class="matriz-table">
        <tr class="matriz-header">
            <td>MÉTRICA</td>
            <td>MM {len_mm1}</td>
            <td>MM {len_mm2}</td>
            <td>MM {len_mm3}</td>
            <td>MM {len_mm4}</td>
            <td>MM {len_mm5}</td>
        </tr>
        <tr>
            <td class="bg-dark">Tendencia</td>
            <td class="{c_ma1}">{'ALCISTA' if c_last > last['ma1'] else 'BAJISTA'}</td>
            <td class="{c_ma2}">{'ALCISTA' if c_last > last['ma2'] else 'BAJISTA'}</td>
            <td class="{c_ma3}">{'ALCISTA' if c_last > last['ma3'] else 'BAJISTA'}</td>
            <td class="{c_ma4}">{'ALCISTA' if c_last > last['ma4'] else 'BAJISTA'}</td>
            <td class="{c_ma5}">{'ALCISTA' if c_last > last['ma5'] else 'BAJISTA'}</td>
        </tr>
        <tr>
            <td class="bg-navy">FILTROS OPT.</td>
            <td class="{c_adx}">ADX ({last['adx']:.1f})</td>
            <td class="bg-dark">RÉGIMEN</td>
            <td class="{c_reg}">{'TENDENCIA' if is_trending else 'RANGO LATERAL'}</td>
            <td class="bg-dark">CONF. MTF</td>
            <td class="{c_ma2}">{'ALCISTA' if c_last > last['ma2'] else 'BAJISTA'}</td>
        </tr>
        <tr>
            <td class="bg-orange">ORACLE</td>
            <td class="bg-dark">Estándar</td>
            <td class="bg-dark">VALOR WT1</td>
            <td class="bg-dark">{last['ora_wt1']:.2f}</td>
            <td class="bg-dark">ESTADO ORACLE</td>
            <td class="{c_ora}">{'COMPRA' if last['ora_wt1'] > last['ora_wt2'] else 'VENTA'}</td>
        </tr>
        <tr>
            <td class="bg-navy">SCORE BOT</td>
            <td class="{c_score}">{score} / 100</td>
            <td class="bg-dark">ESTADO RSI</td>
            <td class="bg-dark">{'SOBRECOMPRA' if last['rsi'] > rsi_ob_limit else ('SOBREVENTA' if last['rsi'] < rsi_os_limit else 'NEUTRO')}</td>
            <td class="bg-dark">VALOR RSI</td>
            <td class="bg-dark">{last['rsi']:.1f}</td>
        </tr>
        <tr>
            <td class="bg-gold">SEÑAL BOT</td>
            <td class="{c_sig}">{signal}</td>
            <td class="bg-dark">PRECIO ENTRADA</td>
            <td class="bg-dark">${c_last:.2f}</td>
            <td class="bg-dark">RATIO R:B REAL</td>
            <td class="bg-dark">1 : {fallback_ratio:.1f}</td>
        </tr>
        <tr>
            <td class="bg-purple">GESTIÓN RIESGO</td>
            <td class="bg-red">STOP LOSS (ATR)</td>
            <td class="bg-red">{sl_str}</td>
            <td class="bg-green">TAKE PROFIT</td>
            <td class="bg-green">{tp_str}</td>
            <td class="bg-dark">RIESGO: ATR Dinámico</td>
        </tr>
    </table>
    """
    st.markdown(matriz_html, unsafe_allow_html=True)
else:
    st.warning("No se pudieron obtener datos para el activo seleccionado.")
