import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de la página Streamlit
st.set_page_config(
    page_title="Sistema Scoring - TradingView Style",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS generales para la aplicación
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    
    /* Tabla Matricial */
    .matriz-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 12px;
        color: white;
        margin-top: 15px;
    }
    .matriz-table th, .matriz-table td {
        border: 1px solid #2a2e39;
        padding: 6px;
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

    /* Tarjeta de Información Financiera del Activo */
    .tv-detail-card {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        padding: 12px;
        margin-top: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .tv-detail-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
    .tv-detail-logo { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; background-color: #2a2e39; }
    .tv-detail-title { font-size: 16px; font-weight: bold; color: #ffffff; }
    .tv-detail-sub { font-size: 11px; color: #787b86; margin-bottom: 8px; }
    .tv-detail-price { font-size: 22px; font-weight: bold; color: #ffffff; }
    .tv-detail-change-up { font-size: 13px; font-weight: bold; color: #26a69a; }
    .tv-detail-change-down { font-size: 13px; font-weight: bold; color: #ef5350; }
    .tv-detail-meta { font-size: 10px; color: #787b86; margin-top: 6px; }
    </style>
""", unsafe_allow_html=True)

# Helper para obtener URL del logo dinámico
def get_logo_url(yf_ticker):
    clean_ticker = yf_ticker.replace(".BA", "").replace("^", "").replace("-USD", "")
    return f"https://assets.parqet.com/logos/symbol/{clean_ticker}?format=jpg"

# ==========================================
# INICIALIZACIÓN DE LA BASE DE ACTIVOS Y LISTAS
# ==========================================
if "activos_dict" not in st.session_state:
    st.session_state.activos_dict = {
        # ÍNDICES
        "SPX": {"name": "S&P 500 Index", "tv": "SP:SPX", "yf": "^GSPC", "cat": "Indices"},
        "RSP": {"name": "S&P 500 Equal Weight", "tv": "AMEX:RSP", "yf": "RSP", "cat": "Indices"},
        
        # SECTORES
        "IBB": {"name": "Biotechnology ETF", "tv": "NASDAQ:IBB", "yf": "IBB", "cat": "Sectores"},
        "IGV": {"name": "Software ETF", "tv": "BATS:IGV", "yf": "IGV", "cat": "Sectores"},
        "IHAK": {"name": "Cybersecurity ETF", "tv": "NYSEARCA:IHAK", "yf": "IHAK", "cat": "Sectores"},
        "CIBR": {"name": "Cybersecurity ETF", "tv": "NASDAQ:CIBR", "yf": "CIBR", "cat": "Sectores"},
        "ITA": {"name": "U.S. Aerospace & Defense", "tv": "CBOE:ITA", "yf": "ITA", "cat": "Sectores"},
        "IYZ": {"name": "Telecom ETF", "tv": "NYSEARCA:IYZ", "yf": "IYZ", "cat": "Sectores"},
        "SOXX": {"name": "Semiconductor ETF", "tv": "NASDAQ:SOXX", "yf": "SOXX", "cat": "Sectores"},
        "XLB": {"name": "Materials Select Sector", "tv": "AMEX:XLB", "yf": "XLB", "cat": "Sectores"},
        "XLC": {"name": "Communication Services", "tv": "AMEX:XLC", "yf": "XLC", "cat": "Sectores"},
        "XLE": {"name": "Energy Select Sector", "tv": "AMEX:XLE", "yf": "XLE", "cat": "Sectores"},
        "XLF": {"name": "Financial Select Sector", "tv": "AMEX:XLF", "yf": "XLF", "cat": "Sectores"},
        "XLI": {"name": "Industrial Select Sector", "tv": "AMEX:XLI", "yf": "XLI", "cat": "Sectores"},
        "XLK": {"name": "Technology Select Sector", "tv": "AMEX:XLK", "yf": "XLK", "cat": "Sectores"},
        
        # INTERNACIONAL
        "UBER": {"name": "Uber Technologies Inc.", "tv": "NYSE:UBER", "yf": "UBER", "cat": "Internacional"},
        "MCD": {"name": "McDonald's Corp.", "tv": "NYSE:MCD", "yf": "MCD", "cat": "Internacional"},
        "DIS": {"name": "Walt Disney Co.", "tv": "NYSE:DIS", "yf": "DIS", "cat": "Internacional"},
        "NFLX": {"name": "Netflix Inc.", "tv": "NASDAQ:NFLX", "yf": "NFLX", "cat": "Internacional"},
        "NKE": {"name": "Nike Inc.", "tv": "NYSE:NKE", "yf": "NKE", "cat": "Internacional"},
        "BKNG": {"name": "Booking Holdings", "tv": "NASDAQ:BKNG", "yf": "BKNG", "cat": "Internacional"},
        "TSLA": {"name": "Tesla Inc.", "tv": "NASDAQ:TSLA", "yf": "TSLA", "cat": "Internacional"},
        "F": {"name": "Ford Motor Co.", "tv": "NYSE:F", "yf": "F", "cat": "Internacional"},
        "BRK.B": {"name": "Berkshire Hathaway", "tv": "NYSE:BRK.B", "yf": "BRK-B", "cat": "Internacional"},
        "JPM": {"name": "JPMorgan Chase", "tv": "NYSE:JPM", "yf": "JPM", "cat": "Internacional"},
        "V": {"name": "Visa Inc.", "tv": "NYSE:V", "yf": "V", "cat": "Internacional"},
        "MA": {"name": "Mastercard Inc.", "tv": "NYSE:MA", "yf": "MA", "cat": "Internacional"},

        # MERCADO ARGENTINO (BCBA)
        "IMV": {"name": "Índice Merval", "tv": "BCBA:IMV", "yf": "^MERV", "cat": "Mercado Argentino"},
        "YPFD": {"name": "YPF S.A.", "tv": "BCBA:YPFD", "yf": "YPFD.BA", "cat": "Mercado Argentino"},
        "PAMP": {"name": "Pampa Energía", "tv": "BCBA:PAMP", "yf": "PAMP.BA", "cat": "Mercado Argentino"},
        "SUPV": {"name": "Grupo Supervielle", "tv": "BCBA:SUPV", "yf": "SUPV.BA", "cat": "Mercado Argentino"},
        "GGAL": {"name": "Grupo Fin. Galicia", "tv": "BCBA:GGAL", "yf": "GGAL.BA", "cat": "Mercado Argentino"}
    }

if "listas_personalizadas" not in st.session_state:
    st.session_state.listas_personalizadas = {
        "Lista de seguimiento": list(st.session_state.activos_dict.keys()),
        "Lista roja 🚩": ["UBER", "MCD", "NFLX", "TSLA", "YPFD", "GGAL"],
        "BYMA, Ganadoras por cambio %": ["YPFD", "PAMP", "SUPV", "GGAL", "IMV"]
    }

if "lista_activa_sel" not in st.session_state:
    st.session_state.lista_activa_sel = "Lista de seguimiento"

keys_list = st.session_state.listas_personalizadas[st.session_state.lista_activa_sel]

if "idx_activo" not in st.session_state or st.session_state.idx_activo >= len(keys_list):
    st.session_state.idx_activo = 0

# ==========================================
# OBTENCIÓN DE DATOS DE MERCADO
# ==========================================
@st.cache_data(ttl=30)
def obtener_cotizaciones_watchlist(activos_dict):
    symbols = [v["yf"] for v in activos_dict.values()]
    try:
        data = yf.download(symbols, period="2d", interval="1d", progress=False)
        res = {}
        if not data.empty and 'Close' in data:
            closes = data['Close']
            volumes = data['Volume'] if 'Volume' in data else None
            for k, v in activos_dict.items():
                sym = v["yf"]
                if sym in closes.columns or len(symbols) == 1:
                    col = closes[sym] if len(symbols) > 1 else closes
                    col_v = volumes[sym] if (volumes is not None and len(symbols) > 1 and sym in volumes.columns) else None
                    col_valid = col.dropna()
                    if len(col_valid) >= 2:
                        last = float(col_valid.iloc[-1])
                        prev = float(col_valid.iloc[-2])
                        cbo = last - prev
                        cbo_pct = (cbo / prev) * 100.0
                        vol_last = float(col_v.dropna().iloc[-1]) if col_v is not None and not col_v.dropna().empty else 0.0
                        res[k] = {"last": last, "cbo": cbo, "cbo_pct": cbo_pct, "vol": vol_last}
                    elif len(col_valid) == 1:
                        last = float(col_valid.iloc[-1])
                        res[k] = {"last": last, "cbo": 0.0, "cbo_pct": 0.0, "vol": 0.0}
        return res
    except Exception:
        return {}

market_data = obtener_cotizaciones_watchlist(st.session_state.activos_dict)

# ==========================================
# BARRA LATERAL: PARÁMETROS DEL SCORING
# ==========================================
st.sidebar.header("⚙️ Configuración del Scoring")

timeframe_map = {
    "1 Minuto": {"tv": "1", "yf_interval": "1m", "yf_period": "7d"},
    "5 Minutos": {"tv": "5", "yf_interval": "5m", "yf_period": "30d"},
    "15 Minutos": {"tv": "15", "yf_interval": "15m", "yf_period": "60d"},
    "30 Minutos": {"tv": "30", "yf_interval": "30m", "yf_period": "60d"},
    "1 Hora": {"tv": "60", "yf_interval": "1h", "yf_period": "730d"},
    "Diario (1D)": {"tv": "D", "yf_interval": "1d", "yf_period": "5y"},
    "Semanal (1W)": {"tv": "W", "yf_interval": "1wk", "yf_period": "10y"}
}

tf_sel = st.sidebar.selectbox("Temporalidad del Análisis:", list(timeframe_map.keys()), index=5)
tv_tf_code = timeframe_map[tf_sel]["tv"]
yf_interval = timeframe_map[tf_sel]["yf_interval"]
yf_period = timeframe_map[tf_sel]["yf_period"]

with st.sidebar.expander("📈 Configuración Medias Móviles", expanded=False):
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

with st.sidebar.expander("⚙️ Optimizaciones de Estrategia", expanded=False):
    use_atr_risk = st.checkbox("Activar SL/TP Dinámico con ATR", value=True)
    atr_len = st.number_input("Período ATR", value=14, step=1)
    atr_mult_sl = st.number_input("Multiplicador ATR", value=2.0, step=0.1)
    use_adx_filter = st.checkbox("Activar Filtro ADX", value=True)
    adx_len = st.number_input("Período ADX", value=14, step=1)
    adx_th = st.number_input("Umbral ADX", value=20, step=1)
    rsi_ob_limit = st.number_input("Límite RSI Compra", value=70.0, step=1.0)
    rsi_os_limit = st.number_input("Límite RSI Venta", value=30.0, step=1.0)
    fallback_ratio = st.number_input("Ratio R:B por defecto", value=2.0, step=0.1)

with st.sidebar.expander("🎯 SuperTrend & Oracle Oscillator", expanded=False):
    use_st = st.checkbox("Activar SuperTrend", value=True)
    st_period = st.number_input("Período SuperTrend", value=22, step=1)
    st_mult = st.number_input("Multiplicador SuperTrend", value=3.0, step=0.1)
    use_oracle = st.checkbox("Integrar Oracle Oscillator al Score", value=True)

with st.sidebar.expander("➕ / ➖ Gestionar Activos Manuales", expanded=False):
    tab_add, tab_del = st.tabs(["Agregar", "Eliminar"])
    with tab_add:
        n_ticker = st.text_input("Ticker Visible (ej: AAPL):")
        n_name = st.text_input("Nombre de la Empresa:")
        n_tv = st.text_input("Ticker TradingView (ej: NASDAQ:AAPL):")
        n_yf = st.text_input("Ticker Yahoo Finance (ej: AAPL):")
        n_cat = st.selectbox("Categoría:", ["Indices", "Sectores", "Internacional", "Mercado Argentino"])
        if st.button("Guardar Activo"):
            if n_ticker and n_tv and n_yf:
                tick_clean = n_ticker.strip().upper()
                st.session_state.activos_dict[tick_clean] = {
                    "name": n_name.strip(), "tv": n_tv.strip().upper(), "yf": n_yf.strip().upper(), "cat": n_cat
                }
                st.session_state.listas_personalizadas["Lista de seguimiento"].append(tick_clean)
                st.success(f"¡{tick_clean} agregado correctamente con su icono!")
                st.rerun()
    with tab_del:
        b_ticker = st.selectbox("Activo a Borrar:", list(st.session_state.activos_dict.keys()))
        if st.button("Borrar Activo"):
            if len(st.session_state.activos_dict) > 1:
                del st.session_state.activos_dict[b_ticker]
                for l_name in st.session_state.listas_personalizadas:
                    if b_ticker in st.session_state.listas_personalizadas[l_name]:
                        st.session_state.listas_personalizadas[l_name].remove(b_ticker)
                st.session_state.idx_activo = 0
                st.rerun()

# ==========================================
# CÁLCULOS MATEMÁTICOS DE PINE SCRIPT
# ==========================================
@st.cache_data(ttl=60)
def calcular_matriz_pine(symbol_yf, interval, period, 
                         m1, m2, m3, m4, m5,
                         a_len, a_mult, adx_l, adx_t, rsi_ob, rsi_os,
                         st_p, st_m, u_oracle, u_st):
    try:
        df = yf.download(symbol_yf, period=period, interval=interval, progress=False)
        if df.empty or len(df) < 30:
            return None
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        close, high, low, open_p = df['Close'], df['High'], df['Low'], df['Open']
        
        ma1 = close.ewm(span=m1, adjust=False).mean()
        ma2 = close.ewm(span=m2, adjust=False).mean()
        ma3 = close.ewm(span=m3, adjust=False).mean()
        ma4 = close.ewm(span=m4, adjust=False).mean()
        ma5 = close.ewm(span=m5, adjust=False).mean()
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/a_len, adjust=False).mean()
        
        up, down = high.diff(), -low.diff()
        plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0), index=df.index)
        minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0), index=df.index)
        tr_smooth = tr.ewm(alpha=1/adx_l, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/adx_l, adjust=False).mean() / tr_smooth)
        minus_di = 100 * (minus_dm.ewm(alpha=1/adx_l, adjust=False).mean() / tr_smooth)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/adx_l, adjust=False).mean()
        
        bb_basis = close.rolling(window=20).mean()
        bb_dev = 2.0 * close.rolling(window=20).std()
        macd_line = close.ewm(span=8, adjust=False).mean() - close.ewm(span=m2, adjust=False).mean()
        signal_line = macd_line.ewm(span=14, adjust=False).mean()
        
        hl2 = (high + low) / 2
        st_atr = tr.ewm(alpha=1/st_p, adjust=False).mean()
        up_band = hl2 - (st_m * st_atr)
        dn_band = hl2 + (st_m * st_atr)
        st_dir = np.zeros(len(df))
        for i in range(1, len(df)):
            if close.iloc[i] > dn_band.iloc[i-1]:
                st_dir[i] = -1
            elif close.iloc[i] < up_band.iloc[i-1]:
                st_dir[i] = 1
            else:
                st_dir[i] = st_dir[i-1]
        
        sop_val = low.rolling(10).min().iloc[-1]
        
        hlc3 = (high + low + close) / 3
        esa = hlc3.ewm(span=10, adjust=False).mean()
        d = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * d)
        ora_wt1 = ci.ewm(span=21, adjust=False).mean()
        ora_wt2 = ora_wt1.rolling(window=4).mean()
        
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
        bbm_l = float(bb_basis.iloc[-1])
        
        score = 0
        if use_mm5 and c_last > ma5_l: score += 10
        if use_mm3 and c_last > ma3_l: score += 5
        if use_mm1 and use_mm2 and ma1_l > ma2_l: score += 5
        if use_mm1 and c_last > ma1_l: score += 5
        if c_last > sop_val: score += 10
        if u_st and st_dir[-1] < 0: score += 10
        if use_mm2 and c_last > ma2_l: score += 5
        if rsi_l >= 50 and rsi_l <= rsi_ob: score += 10
        if macd_l > sig_l: score += 5
        if c_last > bbm_l: score += 5
        if u_oracle:
            if wt1_l > wt2_l: score += 10
            if wt1_l > 0: score += 5
            if wt1_l < 40.0: score += 5
        score += patron_pts
        
        is_trending = (not use_adx_filter) or (adx_l >= adx_t)
        rsi_ok = (rsi_l < rsi_ob)
        
        if score >= 75 and is_trending and rsi_ok:
            signal = "LONG"
            sl = c_last - (atr_l * a_mult)
            tp = c_last + ((c_last - sl) * fallback_ratio)
        elif score <= 25 and is_trending:
            signal = "SHORT"
            sl = c_last + (atr_l * a_mult)
            tp = c_last - ((sl - c_last) * fallback_ratio)
        else:
            signal = "ESPERA"
            sl, tp = None, None
            
        return {
            "precio": c_last, "score": score, "signal": signal,
            "rsi": rsi_l, "adx": adx_l, "wt1": wt1_l, "wt2": wt2_l,
            "patron": patron_nombre, "desc_patron": desc_patron, "patron_pts": patron_pts,
            "ma1": ma1_l, "ma2": ma2_l, "ma3": ma3_l, "ma4": ma4_l, "ma5": ma5_l,
            "macd": macd_l, "sig": sig_l, "sl": sl, "tp": tp,
            "is_trending": is_trending
        }
    except Exception:
        return None

# ==========================================
# LAYOUT PRINCIPAL (75% GRÁFICO / 25% WATCHLIST)
# ==========================================
col_main, col_watchlist = st.columns([0.75, 0.25])

curr_key = keys_list[st.session_state.idx_activo]
curr_item = st.session_state.activos_dict[curr_key]

tv_symbol = curr_item["tv"]
yf_symbol = curr_item["yf"]

# PANEL IZQUIERDO: GRÁFICO Y TABLA MATRICIAL
with col_main:
    st.markdown(f"### 📊 {curr_key} - {curr_item['name']} ({curr_item['cat']})")
    
    template_tv = """
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_chart" style="height:500px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "SYMBOL_PLACEHOLDER",
          "interval": "TIMEFRAME_PLACEHOLDER",
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
        });
      </script>
    </div>
    """
    tradingview_html = template_tv.replace("SYMBOL_PLACEHOLDER", tv_symbol).replace("TIMEFRAME_PLACEHOLDER", tv_tf_code)
    components.html(tradingview_html, height=510)
    
    res = calcular_matriz_pine(
        yf_symbol, yf_interval, yf_period,
        len_mm1, len_mm2, len_mm3, len_mm4, len_mm5,
        atr_len, atr_mult_sl, adx_len, adx_th, rsi_ob_limit, rsi_os_limit,
        st_period, st_mult, use_oracle, use_st
    )
    
    if res:
        c_ma1 = "bg-green" if res['precio'] > res['ma1'] else "bg-red"
        t_ma1 = "ALCISTA" if res['precio'] > res['ma1'] else "BAJISTA"
        c_ma2 = "bg-green" if res['precio'] > res['ma2'] else "bg-red"
        t_ma2 = "ALCISTA" if res['precio'] > res['ma2'] else "BAJISTA"
        c_ma3 = "bg-green" if res['precio'] > res['ma3'] else "bg-red"
        t_ma3 = "ALCISTA" if res['precio'] > res['ma3'] else "BAJISTA"
        c_ma4 = "bg-green" if res['precio'] > res['ma4'] else "bg-red"
        t_ma4 = "ALCISTA" if res['precio'] > res['ma4'] else "BAJISTA"
        c_ma5 = "bg-green" if res['precio'] > res['ma5'] else "bg-red"
        t_ma5 = "ALCISTA" if res['precio'] > res['ma5'] else "BAJISTA"

        c_adx = "bg-green" if res['is_trending'] else "bg-red"
        c_reg = "bg-teal" if res['is_trending'] else "bg-orange"
        t_reg = "TENDENCIA" if res['is_trending'] else "RANGO LATERAL"

        c_ora = "bg-green" if res['wt1'] > res['wt2'] else "bg-red"
        t_ora = "COMPRA" if res['wt1'] > res['wt2'] else "VENTA"

        c_score = "bg-green" if res['score'] >= 75 else ("bg-red" if res['score'] <= 25 else "bg-orange")
        t_rsi = "SOBRECOMPRA" if res['rsi'] > rsi_ob_limit else ("SOBREVENTA" if res['rsi'] < rsi_os_limit else "NEUTRO")

        c_sig = "bg-green" if res['signal'] == "LONG" else ("bg-red" if res['signal'] == "SHORT" else "bg-dark")

        sl_str = f"${res['sl']:.2f}" if res['sl'] is not None else "N/A"
        tp_str = f"${res['tp']:.2f}" if res['tp'] is not None else "N/A"

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
                <td class="{c_ma1}">{t_ma1}</td>
                <td class="{c_ma2}">{t_ma2}</td>
                <td class="{c_ma3}">{t_ma3}</td>
                <td class="{c_ma4}">{t_ma4}</td>
                <td class="{c_ma5}">{t_ma5}</td>
            </tr>
            <tr>
                <td class="bg-navy">FILTROS OPT.</td>
                <td class="{c_adx}">ADX ({res['adx']:.1f})</td>
                <td class="bg-dark">RÉGIMEN</td>
                <td class="{c_reg}">{t_reg}</td>
                <td class="bg-dark">CONF. MTF</td>
                <td class="{c_ma2}">{t_ma2}</td>
            </tr>
            <tr>
                <td class="bg-orange">ORACLE</td>
                <td class="bg-dark">Estándar</td>
                <td class="bg-dark">VALOR WT1</td>
                <td class="bg-dark">{res['wt1']:.2f}</td>
                <td class="bg-dark">ESTADO ORACLE</td>
                <td class="{c_ora}">{t_ora}</td>
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
                <td class="{c_score}">{res['score']} / 100</td>
                <td class="bg-dark">ESTADO RSI</td>
                <td class="bg-dark">{t_rsi}</td>
                <td class="bg-dark">VALOR RSI</td>
                <td class="bg-dark">{res['rsi']:.1f}</td>
            </tr>
            <tr>
                <td class="bg-gold">SEÑAL BOT</td>
                <td class="{c_sig}">{res['signal']}</td>
                <td class="bg-dark">PRECIO ENTRADA</td>
                <td class="bg-dark">${res['precio']:.2f}</td>
                <td class="bg-dark">RATIO R:B REAL</td>
                <td class="bg-dark">1 : {fallback_ratio:.1f}</td>
            </tr>
            <tr>
                <td class="bg-purple">GESTIÓN RIESGO</td>
                <td class="bg-red">STOP LOSS (ATR)</td>
                <td class="bg-red">{sl_str}</td>
                <td class="bg-green">TAKE PROFIT</td>
                <td class="bg-green">{tp_str}</td>
                <td class="bg-dark">RIESGO: {atr_mult_sl:.1f}x ATR</td>
            </tr>
        </table>
        """
        st.markdown(matriz_html, unsafe_allow_html=True)

# PANEL DERECHO: WATCHLIST TIPO TRADINGVIEW CON ICONOS AUTOMÁTICOS
with col_watchlist:
    lista_sel = st.selectbox(
        "📌 Selector de Lista / Banderas:",
        options=list(st.session_state.listas_personalizadas.keys()),
        index=list(st.session_state.listas_personalizadas.keys()).index(st.session_state.lista_activa_sel)
    )

    if lista_sel != st.session_state.lista_activa_sel:
        st.session_state.lista_activa_sel = lista_sel
        st.session_state.idx_activo = 0
        st.rerun()

    with st.popover("⚙️ Opciones de Lista"):
        st.markdown("### 📋 Gestión de Lista")
        st.button("🔔 Añadir alerta a la lista...")
        st.button("📑 Hacer una copia...")
        st.button("✏️ Cambiar el nombre")
        st.button("➕ Añadir sección")
        st.button("🗑️ Borrar lista")
        st.divider()
        st.button("✨ Crear nueva lista...")
        st.button("📂 Cargar lista...")

    col_up, col_dn = st.columns(2)
    with col_up:
        if st.button("⬆️ Anterior", use_container_width=True):
            st.session_state.idx_activo = (st.session_state.idx_activo - 1) % len(keys_list)
            st.rerun()
    with col_dn:
        if st.button("⬇️ Siguiente", use_container_width=True):
            st.session_state.idx_activo = (st.session_state.idx_activo + 1) % len(keys_list)
            st.rerun()

    selected_ticker = st.selectbox(
        "Activo Seleccionado:",
        options=keys_list,
        index=st.session_state.idx_activo,
        key="watchlist_select"
    )

    if keys_list.index(selected_ticker) != st.session_state.idx_activo:
        st.session_state.idx_activo = keys_list.index(selected_ticker)
        st.rerun()

    # Generación de Filas HTML con Iconos Automáticos
    html_rows = ""
    for k in keys_list:
        m = market_data.get(k, {"last": 0.0, "cbo": 0.0, "cbo_pct": 0.0, "vol": 0.0})
        item_info = st.session_state.activos_dict.get(k, {"yf": k})
        logo_url = get_logo_url(item_info["yf"])
        
        is_sel = "tv-row-selected" if k == curr_key else ""
        c_class = "val-up" if m["cbo"] >= 0 else "val-down"
        sign = "+" if m["cbo"] >= 0 else ""
        
        html_rows += f"""
        <tr class="tv-watchlist-row {is_sel}" data-ticker="{k}">
            <td class="tv-cell-sym">
                <img src="{logo_url}" class="tv-icon" onerror="this.src='https://via.placeholder.com/18/2a2e39/ffffff?text={k[0]}';"/>
                <span>{k}</span>
            </td>
            <td class="tv-cell-val">{m['last']:.2f}</td>
            <td class="tv-cell-val {c_class}">{sign}{m['cbo']:.2f}</td>
            <td class="tv-cell-val {c_class}">{sign}{m['cbo_pct']:.2f}%</td>
        </tr>
        """

    watchlist_full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            background-color: #0e1117;
            color: #d1d4dc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            user-select: none;
        }}
        .tv-watchlist-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}
        .tv-watchlist-table th {{
            color: #787b86;
            font-weight: 600;
            text-align: right;
            padding: 6px 4px;
            border-bottom: 1px solid #2a2e39;
            position: sticky;
            top: 0;
            background-color: #131722;
        }}
        .tv-watchlist-table th:first-child {{ text-align: left; }}
        .tv-watchlist-row {{
            cursor: pointer;
            border-bottom: 1px solid #1e222d;
        }}
        .tv-watchlist-row:hover {{ background-color: #2a2e39; }}
        .tv-row-selected {{ background-color: #1e222d; border-left: 3px solid #2962ff; }}
        .tv-cell-sym {{
            font-weight: bold;
            color: #ffffff;
            text-align: left;
            padding: 6px 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .tv-icon {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            object-fit: cover;
            background-color: #2a2e39;
        }}
        .tv-cell-val {{ text-align: right; padding: 6px 4px; }}
        .val-up {{ color: #26a69a; }}
        .val-down {{ color: #ef5350; }}
        
        #context-menu {{
            position: fixed;
            display: none;
            background-color: #1e222d;
            border: 1px solid #363c4e;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            border-radius: 4px;
            padding: 5px 0;
            z-index: 1000;
            width: 180px;
        }}
        .menu-item {{
            padding: 8px 12px;
            font-size: 12px;
            color: #d1d4dc;
            cursor: pointer;
        }}
        .menu-item:hover {{
            background-color: #2962ff;
            color: #ffffff;
        }}
    </style>
    </head>
    <body>
        <div style="height:320px; overflow-y:auto; border:1px solid #2a2e39; border-radius:4px;">
            <table class="tv-watchlist-table">
                <thead>
                    <tr>
                        <th>Símbolo</th>
                        <th>Última</th>
                        <th>Cbo</th>
                        <th>Cbo %</th>
                    </tr>
                </thead>
                <tbody>
                    {html_rows}
                </tbody>
            </table>
        </div>

        <div id="context-menu">
            <div class="menu-item" onclick="alert('Marcar activo')">🚩 Marcar Bandera</div>
            <div class="menu-item" onclick="alert('Añadir a lista roja')">📌 Añadir a Lista Roja</div>
            <div class="menu-item" onclick="alert('Añadir Nota')">📝 Añadir Nota</div>
            <div class="menu-item" onclick="alert('Ajustar Parámetros')">⚙️ Configuración</div>
        </div>

        <script>
            const menu = document.getElementById('context-menu');
            document.addEventListener('click', () => menu.style.display = 'none');
            document.querySelectorAll('.tv-watchlist-row').forEach(row => {{
                row.addEventListener('contextmenu', (e) => {{
                    e.preventDefault();
                    menu.style.top = `${{e.clientY}}px`;
                    menu.style.left = `${{e.clientX}}px`;
                    menu.style.display = 'block';
                }});
            }});
        </script>
    </body>
    </html>
    """
    components.html(watchlist_full_html, height=330)

    # Tarjeta de Detalle con Icono del Activo Seleccionado
    curr_m = market_data.get(curr_key, {"last": 0.0, "cbo": 0.0, "cbo_pct": 0.0, "vol": 0.0})
    change_style = "tv-detail-change-up" if curr_m["cbo"] >= 0 else "tv-detail-change-down"
    sign_m = "+" if curr_m["cbo"] >= 0 else ""
    curr_logo = get_logo_url(curr_item["yf"])

    st.markdown(f"""
        <div class="tv-detail-card">
            <div class="tv-detail-header">
                <img src="{curr_logo}" class="tv-detail-logo" onerror="this.src='https://via.placeholder.com/28/2a2e39/ffffff?text={curr_key[0]}';"/>
                <div>
                    <div class="tv-detail-title">{curr_key}</div>
                    <div class="tv-detail-sub">{curr_item['name']} • {curr_item['cat']}</div>
                </div>
            </div>
            <div class="tv-detail-price">${curr_m['last']:.2f} USD</div>
            <div class="{change_style}">{sign_m}{curr_m['cbo']:.2f} ({sign_m}{curr_m['cbo_pct']:.2f}%)</div>
            <div class="tv-detail-meta">Volumen Medio (30d): {curr_m['vol']/1e6:.2f}M</div>
        </div>
    """, unsafe_allow_html=True)
