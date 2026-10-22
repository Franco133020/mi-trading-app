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

# Estilos CSS generales y réplica visual estilo TradingView
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    
    /* Tabla Matricial Inferior */
    .matriz-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 11px;
        color: white;
        margin-top: 10px;
    }
    .matriz-table th, .matriz-table td {
        border: 1px solid #2a2e39;
        padding: 5px;
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
    
    /* Tarjeta Inferior de Detalle */
    .tv-detail-card {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 4px;
        padding: 12px;
        margin-top: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .tv-detail-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
    .tv-detail-title { font-size: 16px; font-weight: bold; color: #ffffff; }
    .tv-detail-sub { font-size: 11px; color: #787b86; }
    .tv-detail-price { font-size: 22px; font-weight: bold; color: #ffffff; margin-top: 4px; }
    .val-up { color: #26a69a; font-weight: bold; font-size: 13px; }
    .val-down { color: #ef5350; font-weight: bold; font-size: 13px; }
    .tv-detail-meta { font-size: 11px; color: #787b86; margin-top: 6px; display: flex; justify-content: space-between; }
    </style>
""", unsafe_allow_html=True)

# Helper para obtener el LOGO OFICIAL ORIGINAL desde CDN de TradingView / Parqet
def get_logo_url(ticker_key):
    clean = ticker_key.replace("USD", "").replace("M", "").replace("2M", "")
    if clean in ["US500", "MERV"]:
        return f"https://s3-symbol-logo.tradingview.com/indices/{clean.lower()}--big.svg"
    elif clean in ["BTC", "ETH"]:
        return f"https://s3-symbol-logo.tradingview.com/crypto/XTVC{clean}--big.svg"
    return f"https://assets.parqet.com/logos/symbol/{clean}?format=png"

# ==========================================
# BASE COMPLETA DE ACTIVOS SOLICITADOS
# ==========================================
if "activos_dict" not in st.session_state:
    st.session_state.activos_dict = {
        # ÍNDICES Y CRIPTO
        "US500": {"name": "S&P 500 Index", "tv": "FOREXCOM:SPXUSD", "yf": "^GSPC", "cat": "Índices"},
        "BTCUSD": {"name": "Bitcoin / USD", "tv": "BINANCE:BTCUSDT", "yf": "BTC-USD", "cat": "Cripto"},
        "ETHUSD": {"name": "Ethereum / USD", "tv": "BINANCE:ETHUSDT", "yf": "ETH-USD", "cat": "Cripto"},
        "GC": {"name": "Gold Futures", "tv": "COMEX:GC1!", "yf": "GC=F", "cat": "Commodities"},
        "SH": {"name": "ProShares Short S&P500", "tv": "NYSEARCA:SH", "yf": "SH", "cat": "ETFs"},
        "EWZ": {"name": "iShares MSCI Brazil ETF", "tv": "NYSEARCA:EWZ", "yf": "EWZ", "cat": "ETFs"},

        # TECNOLOGÍA & CRECIMIENTO (US)
        "AAPL": {"name": "Apple Inc.", "tv": "NASDAQ:AAPL", "yf": "AAPL", "cat": "Tecnología"},
        "MSFT": {"name": "Microsoft Corp.", "tv": "NASDAQ:MSFT", "yf": "MSFT", "cat": "Tecnología"},
        "GOOGL": {"name": "Alphabet Inc.", "tv": "NASDAQ:GOOGL", "yf": "GOOGL", "cat": "Tecnología"},
        "NVDA": {"name": "NVIDIA Corp.", "tv": "NASDAQ:NVDA", "yf": "NVDA", "cat": "Semiconductores"},
        "AMD": {"name": "Advanced Micro Devices", "tv": "NASDAQ:AMD", "yf": "AMD", "cat": "Semiconductores"},
        "INTC": {"name": "Intel Corp.", "tv": "NASDAQ:INTC", "yf": "INTC", "cat": "Semiconductores"},
        "MU": {"name": "Micron Technology", "tv": "NASDAQ:MU", "yf": "MU", "cat": "Semiconductores"},
        "AMZN": {"name": "Amazon.com Inc.", "tv": "NASDAQ:AMZN", "yf": "AMZN", "cat": "E-Commerce"},
        "META": {"name": "Meta Platforms", "tv": "NASDAQ:META", "yf": "META", "cat": "Tecnología"},
        "TSLA": {"name": "Tesla Inc.", "tv": "NASDAQ:TSLA", "yf": "TSLA", "cat": "Automotriz"},
        "MSTR": {"name": "MicroStrategy Inc.", "tv": "NASDAQ:MSTR", "yf": "MSTR", "cat": "Tecnología"},
        "PYPL": {"name": "PayPal Holdings", "tv": "NASDAQ:PYPL", "yf": "PYPL", "cat": "Fintech"},
        "UPST": {"name": "Upstart Holdings", "tv": "NASDAQ:UPST", "yf": "UPST", "cat": "Fintech"},
        "GLOB": {"name": "Globant S.A.", "tv": "NYSE:GLOB", "yf": "GLOB", "cat": "Software"},
        "CSCO": {"name": "Cisco Systems", "tv": "NASDAQ:CSCO", "yf": "CSCO", "cat": "Redes"},
        "IBM": {"name": "IBM Corp.", "tv": "NYSE:IBM", "yf": "IBM", "cat": "Tecnología"},
        "SPOT": {"name": "Spotify Technology", "tv": "NYSE:SPOT", "yf": "SPOT", "cat": "Entretenimiento"},
        "CRM": {"name": "Salesforce Inc.", "tv": "NYSE:CRM", "yf": "CRM", "cat": "Software"},
        "ACN": {"name": "Accenture plc", "tv": "NYSE:ACN", "yf": "ACN", "cat": "Consultoría"},
        "ADBE": {"name": "Adobe Inc.", "tv": "NASDAQ:ADBE", "yf": "ADBE", "cat": "Software"},
        "PLTR": {"name": "Palantir Technologies", "tv": "NYSE:PLTR", "yf": "PLTR", "cat": "Software"},
        "CRCL": {"name": "Circle K / Circle", "tv": "NYSE:CRCL", "yf": "CRCL", "cat": "Fintech"},
        "RGTI": {"name": "Rigetti Computing", "tv": "NASDAQ:RGTI", "yf": "RGTI", "cat": "Cuántica"},
        "MELI": {"name": "MercadoLibre Inc.", "tv": "NASDAQ:MELI", "yf": "MELI", "cat": "E-Commerce"},
        "BABA": {"name": "Alibaba Group", "tv": "NYSE:BABA", "yf": "BABA", "cat": "E-Commerce"},

        # CONSUMO, ENTRETENIMIENTO Y CONSUMO MASIVO
        "NFLX": {"name": "Netflix Inc.", "tv": "NASDAQ:NFLX", "yf": "NFLX", "cat": "Streaming"},
        "DIS": {"name": "Walt Disney Co.", "tv": "NYSE:DIS", "yf": "DIS", "cat": "Entretenimiento"},
        "UBER": {"name": "Uber Technologies", "tv": "NYSE:UBER", "yf": "UBER", "cat": "Movilidad"},
        "MCD": {"name": "McDonald's Corp.", "tv": "NYSE:MCD", "yf": "MCD", "cat": "Consumo"},
        "KO": {"name": "Coca-Cola Co.", "tv": "NYSE:KO", "yf": "KO", "cat": "Bebidas"},
        "PEP": {"name": "PepsiCo Inc.", "tv": "NASDAQ:PEP", "yf": "PEP", "cat": "Bebidas"},
        "CL": {"name": "Colgate-Palmolive", "tv": "NYSE:CL", "yf": "CL", "cat": "Consumo Masivo"},
        "NKE": {"name": "Nike Inc.", "tv": "NYSE:NKE", "yf": "NKE", "cat": "Consumo"},
        "GM": {"name": "General Motors", "tv": "NYSE:GM", "yf": "GM", "cat": "Automotriz"},
        "WMT": {"name": "Walmart Inc.", "tv": "NYSE:WMT", "yf": "WMT", "cat": "Retail"},
        "ABNB": {"name": "Airbnb Inc.", "tv": "NASDAQ:ABNB", "yf": "ABNB", "cat": "Turismo"},
        "NU": {"name": "Nu Holdings (Nubank)", "tv": "NYSE:NU", "yf": "NU", "cat": "Fintech"},

        # MERCADO ARGENTINO (BYMA / ADRs)
        "MERV": {"name": "Índice Merval", "tv": "BCBA:IMV", "yf": "^MERV", "cat": "Mercado Argentino"},
        "BYMAM": {"name": "Bolsas y Mercados Arg.", "tv": "BCBA:BYMA", "yf": "BYMA.BA", "cat": "Mercado Argentino"},
        "BBAR": {"name": "Banco BBVA Argentina", "tv": "NYSE:BBAR", "yf": "BBAR", "cat": "Bancos Arg."},
        "GGAL": {"name": "Grupo Fin. Galicia", "tv": "NASDAQ:GGAL", "yf": "GGAL", "cat": "Bancos Arg."},
        "SUPV": {"name": "Grupo Supervielle", "tv": "NYSE:SUPV", "yf": "SUPV", "cat": "Bancos Arg."},
        "BMA": {"name": "Banco Macro", "tv": "NYSE:BMA", "yf": "BMA", "cat": "Bancos Arg."},
        "VALO": {"name": "Grupo Financiero Valores", "tv": "BCBA:VALO", "yf": "VALO.BA", "cat": "Bancos Arg."},
        "CEPU": {"name": "Central Puerto", "tv": "NYSE:CEPU", "yf": "CEPU", "cat": "Energía Arg."},
        "YPF": {"name": "YPF S.A.", "tv": "NYSE:YPF", "yf": "YPF", "cat": "Energía Arg."},
        "PAM": {"name": "Pampa Energía", "tv": "NYSE:PAM", "yf": "PAM", "cat": "Energía Arg."},
        "VIST": {"name": "Vista Energy", "tv": "NYSE:VIST", "yf": "VIST", "cat": "Energía Arg."},
        "IRS": {"name": "Irsa Inversiones y Rep.", "tv": "NYSE:IRS", "yf": "IRS", "cat": "Bienes Raíces Arg."},
        "ALUA": {"name": "Aluar Aluminio Arg.", "tv": "BCBA:ALUA", "yf": "ALUA.BA", "cat": "Industria Arg."},
        "EDN": {"name": "Edenor S.A.", "tv": "NYSE:EDN", "yf": "EDN", "cat": "Energía Arg."},
        "TGS": {"name": "Transportadora Gas del Sur", "tv": "NYSE:TGS", "yf": "TGS", "cat": "Energía Arg."},
        "TGSU2M": {"name": "TGS Clase B (BYMA)", "tv": "BCBA:TGSU2", "yf": "TGSU2.BA", "cat": "Energía Arg."},
        "TRANM": {"name": "Transener (BYMA)", "tv": "BCBA:TRAN", "yf": "TRAN.BA", "cat": "Energía Arg."},
        "LOMA": {"name": "Loma Negra Cemento", "tv": "NYSE:LOMA", "yf": "LOMA", "cat": "Construcción Arg."},
        "PBR": {"name": "Petrobras", "tv": "NYSE:PBR", "yf": "PBR", "cat": "Energía Brasil"}
    }

if "listas_personalizadas" not in st.session_state:
    st.session_state.listas_personalizadas = {
        "Lista Completa": list(st.session_state.activos_dict.keys()),
        "Tecnología & Crecimiento": ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD", "TSLA", "MSTR", "PLTR", "ADBE"],
        "Mercado Argentino (BYMA / ADRs)": ["MERV", "YPF", "PAM", "GGAL", "BMA", "VIST", "CEPU", "TGS", "ALUA", "EDN"],
        "Cripto & Commodities": ["BTCUSD", "ETHUSD", "GC", "MSTR"]
    }

if "lista_activa_sel" not in st.session_state:
    st.session_state.lista_activa_sel = "Lista Completa"

keys_list = st.session_state.listas_personalizadas[st.session_state.lista_activa_sel]
if "idx_activo" not in st.session_state or st.session_state.idx_activo >= len(keys_list):
    st.session_state.idx_activo = 0

# ==========================================
# DATOS DE MERCADO EN TIEMPO REAL (YFINANCE)
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
# BARRA LATERAL DE PARÁMETROS
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

with st.sidebar.expander("📈 Medias Móviles", expanded=False):
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

with st.sidebar.expander("⚙️ Filtros de Estrategia", expanded=False):
    use_atr_risk = st.checkbox("Activar SL/TP Dinámico con ATR", value=True)
    atr_len = st.number_input("Período ATR", value=14, step=1)
    atr_mult_sl = st.number_input("Multiplicador ATR", value=2.0, step=0.1)
    use_adx_filter = st.checkbox("Activar Filtro ADX", value=True)
    adx_len = st.number_input("Período ADX", value=14, step=1)
    adx_th = st.number_input("Umbral ADX", value=20, step=1)
    rsi_ob_limit = st.number_input("Límite RSI Compra", value=70.0, step=1.0)
    rsi_os_limit = st.number_input("Límite RSI Venta", value=30.0, step=1.0)
    fallback_ratio = st.number_input("Ratio R:B por defecto", value=2.0, step=0.1)

with st.sidebar.expander("🎯 SuperTrend & Oracle", expanded=False):
    use_st = st.checkbox("Activar SuperTrend", value=True)
    st_period = st.number_input("Período SuperTrend", value=22, step=1)
    st_mult = st.number_input("Multiplicador SuperTrend", value=3.0, step=0.1)
    use_oracle = st.checkbox("Integrar Oracle Oscillator", value=True)

# ==========================================
# CÁLCULOS MATEMÁTICOS DEL PINE SCRIPT
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
            
        close, high, low, open_p, volume = df['Close'], df['High'], df['Low'], df['Open'], df['Volume']
        
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

        ret_c = close.pct_change()
        vol_shift = volume.shift(1)
        nvi = pd.Series(1000.0, index=df.index)
        for i in range(1, len(df)):
            if volume.iloc[i] < vol_shift.iloc[i]:
                nvi.iloc[i] = nvi.iloc[i-1] + (ret_c.iloc[i] * nvi.iloc[i-1])
            else:
                nvi.iloc[i] = nvi.iloc[i-1]
        nvi_ema = nvi.ewm(span=15, adjust=False).mean()
        nvi_hi = nvi_ema.rolling(90).max()
        nvi_lo = nvi_ema.rolling(90).min()
        k_azul = np.where(nvi_hi != nvi_lo, (nvi - nvi_ema) * 100 / (nvi_hi - nvi_lo), 0)
        
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
        k_azul_l = float(k_azul[-1])
        
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
        if k_azul_l > 0: score += 5
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
# LAYOUT DUAL (75% GRÁFICO / 25% WATCHLIST)
# ==========================================
col_main, col_watchlist = st.columns([0.75, 0.25])

curr_key = keys_list[st.session_state.idx_activo]
curr_item = st.session_state.activos_dict[curr_key]
tv_symbol = curr_item["tv"]
yf_symbol = curr_item["yf"]

# --- PANEL IZQUIERDO: WIDGET OFICIAL DE TRADINGVIEW + MATRIZ ---
with col_main:
    st.markdown(f"### 📊 {curr_key} - {curr_item['name']} ({curr_item['cat']})")
    
    # Widget embebible oficial de TradingView (previene error de conexión)
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

# --- PANEL DERECHO: WATCHLIST SINCRONIZADA E INTERACTIVA ---
with col_watchlist:
    lista_sel = st.selectbox(
        "📌 Lista Activa:",
        options=list(st.session_state.listas_personalizadas.keys()),
        index=list(st.session_state.listas_personalizadas.keys()).index(st.session_state.lista_activa_sel)
    )
    if lista_sel != st.session_state.lista_activa_sel:
        st.session_state.lista_activa_sel = lista_sel
        st.session_state.idx_activo = 0
        st.rerun()

    selected_option = st.selectbox(
        "🔍 Seleccionar Activo:",
        options=keys_list,
        index=st.session_state.idx_activo
    )
    
    selected_idx = keys_list.index(selected_option)
    if selected_idx != st.session_state.idx_activo:
        st.session_state.idx_activo = selected_idx
        st.rerun()

    # DATAFRAME DE SEGUIMIENTO CON ESTILOS
    wl_data = []
    for k in keys_list:
        m = market_data.get(k, {"last": 0.0, "cbo": 0.0, "cbo_pct": 0.0})
        sign = "+" if m["cbo"] >= 0 else ""
        wl_data.append({
            "Símbolo": k,
            "Última": f"${m['last']:.2f}",
            "Cbo": f"{sign}{m['cbo']:.2f}",
            "Cambio %": f"{sign}{m['cbo_pct']:.2f}%"
        })

    df_wl = pd.DataFrame(wl_data)
    
    def color_variacion(val):
        if str(val).startswith("+"):
            return "color: #26a69a; font-weight: bold;"
        elif str(val).startswith("-"):
            return "color: #ef5350; font-weight: bold;"
        return ""

    styled_df = df_wl.style.map(color_variacion, subset=["Cbo", "Cambio %"])

    # SELECCIÓN INTERACTIVA MEDIANTE CLIC EN FILAS
    event = st.dataframe(
        styled_df,
        use_container_width=True,
        height=360,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if event and "rows" in event.selection and len(event.selection["rows"]) > 0:
        clicked_row_idx = event.selection["rows"][0]
        if clicked_row_idx != st.session_state.idx_activo:
            st.session_state.idx_activo = clicked_row_idx
            st.rerun()

    # TARJETA INFERIOR DE DETALLE CON LOGO OFICIAL
    curr_m = market_data.get(curr_key, {"last": 0.0, "cbo": 0.0, "cbo_pct": 0.0, "vol": 0.0})
    change_style = "val-up" if curr_m["cbo"] >= 0 else "val-down"
    sign_m = "+" if curr_m["cbo"] >= 0 else ""
    curr_logo = get_logo_url(curr_key)

    st.markdown(f"""
        <div class="tv-detail-card">
            <div class="tv-detail-header">
                <img src="{curr_logo}" style="width:32px;height:32px;border-radius:50%;object-fit:contain;background-color:#1e222d;padding:2px;" onerror="this.src='https://via.placeholder.com/32/2a2e39/ffffff?text={curr_key[0]}';"/>
                <div>
                    <div class="tv-detail-title">{curr_key}</div>
                    <div class="tv-detail-sub">{curr_item['name']} • {curr_item['cat']}</div>
                </div>
            </div>
            <div class="tv-detail-price">${curr_m['last']:.2f} USD</div>
            <div class="{change_style}">
                {sign_m}{curr_m['cbo']:.2f} ({sign_m}{curr_m['cbo_pct']:.2f}%)
            </div>
            <div class="tv-detail-meta">
                <span>Volumen Promedio:</span>
                <span style="color:#ffffff;">{curr_m['vol']/1e6:.2f}M</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
