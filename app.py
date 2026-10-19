import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de la página Streamlit
st.set_page_config(
    page_title="Sistema Scoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alto contraste tipo TradingView
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
# INICIALIZACIÓN DE LA LISTA DE ACTIVOS (SESSION STATE)
# ==========================================
if "activos_dict" not in st.session_state:
    st.session_state.activos_dict = {
        # --- ÍNDICES ---
        "S&P 500 Index (SPX)": {"tv": "SP:SPX", "yf": "^GSPC", "categoria": "Indices"},
        "S&P 500 Equal Weight (RSP)": {"tv": "AMEX:RSP", "yf": "RSP", "categoria": "Indices"},

        # --- SECTORES ---
        "Biotechnology ETF (IBB)": {"tv": "NASDAQ:IBB", "yf": "IBB", "categoria": "Sectores"},
        "Software ETF (IGV)": {"tv": "BATS:IGV", "yf": "IGV", "categoria": "Sectores"},
        "Cybersecurity ETF (IHAK)": {"tv": "NYSEARCA:IHAK", "yf": "IHAK", "categoria": "Sectores"},
        "Cybersecurity ETF (CIBR)": {"tv": "NASDAQ:CIBR", "yf": "CIBR", "categoria": "Sectores"},
        "U.S. Aerospace & Defense (ITA)": {"tv": "CBOE:ITA", "yf": "ITA", "categoria": "Sectores"},
        "Telecom ETF (IYZ)": {"tv": "NYSEARCA:IYZ", "yf": "IYZ", "categoria": "Sectores"},
        "Semiconductor ETF (SOXX)": {"tv": "NASDAQ:SOXX", "yf": "SOXX", "categoria": "Sectores"},
        "Materials Select Sector (XLB)": {"tv": "AMEX:XLB", "yf": "XLB", "categoria": "Sectores"},
        "Communication Services (XLC)": {"tv": "AMEX:XLC", "yf": "XLC", "categoria": "Sectores"},
        "Energy Select Sector (XLE)": {"tv": "AMEX:XLE", "yf": "XLE", "categoria": "Sectores"},
        "Financial Select Sector (XLF)": {"tv": "AMEX:XLF", "yf": "XLF", "categoria": "Sectores"},
        "Industrial Select Sector (XLI)": {"tv": "AMEX:XLI", "yf": "XLI", "categoria": "Sectores"},
        "Technology Select Sector (XLK)": {"tv": "AMEX:XLK", "yf": "XLK", "categoria": "Sectores"},

        # --- INTERNACIONAL ---
        "Nasdaq 100 (QQQ)": {"tv": "NASDAQ:QQQ", "yf": "QQQ", "categoria": "Internacional"},
        "Apple Inc. (AAPL)": {"tv": "NASDAQ:AAPL", "yf": "AAPL", "categoria": "Internacional"},
        "Amazon.com (AMZN)": {"tv": "NASDAQ:AMZN", "yf": "AMZN", "categoria": "Internacional"},
        "Alphabet / Google (GOOGL)": {"tv": "NASDAQ:GOOGL", "yf": "GOOGL", "categoria": "Internacional"},
        "Microsoft (MSFT)": {"tv": "NASDAQ:MSFT", "yf": "MSFT", "categoria": "Internacional"},
        "Meta Platforms (META)": {"tv": "NASDAQ:META", "yf": "META", "categoria": "Internacional"},
        "Tesla (TSLA)": {"tv": "NASDAQ:TSLA", "yf": "TSLA", "categoria": "Internacional"},
        "NVIDIA (NVDA)": {"tv": "NASDAQ:NVDA", "yf": "NVDA", "categoria": "Internacional"},
        "Intel (INTC)": {"tv": "NASDAQ:INTC", "yf": "INTC", "categoria": "Internacional"},
        "Broadcom (AVGO)": {"tv": "NASDAQ:AVGO", "yf": "AVGO", "categoria": "Internacional"},
        "ASML Holding (ASML)": {"tv": "NASDAQ:ASML", "yf": "ASML", "categoria": "Internacional"},
        "Taiwan Semiconductor (TSM)": {"tv": "NYSE:TSM", "yf": "TSM", "categoria": "Internacional"},
        "Advanced Micro Devices (AMD)": {"tv": "NASDAQ:AMD", "yf": "AMD", "categoria": "Internacional"},
        "Marvell Technology (MRVL)": {"tv": "NASDAQ:MRVL", "yf": "MRVL", "categoria": "Internacional"},
        "Arm Holdings (ARM)": {"tv": "NASDAQ:ARM", "yf": "ARM", "categoria": "Internacional"},
        "Micron Technology (MU)": {"tv": "NASDAQ:MU", "yf": "MU", "categoria": "Internacional"},
        "Lam Research (LRCX)": {"tv": "NASDAQ:LRCX", "yf": "LRCX", "categoria": "Internacional"},
        "Oracle (ORCL)": {"tv": "NYSE:ORCL", "yf": "ORCL", "categoria": "Internacional"},
        "IBM": {"tv": "NYSE:IBM", "yf": "IBM", "categoria": "Internacional"},
        "Spotify (SPOT)": {"tv": "NYSE:SPOT", "yf": "SPOT", "categoria": "Internacional"},
        "Salesforce (CRM)": {"tv": "NYSE:CRM", "yf": "CRM", "categoria": "Internacional"},
        "Accenture (ACN)": {"tv": "NYSE:ACN", "yf": "ACN", "categoria": "Internacional"},
        "Adobe (ADBE)": {"tv": "NASDAQ:ADBE", "yf": "ADBE", "categoria": "Internacional"},
        "Palantir (PLTR)": {"tv": "NYSE:PLTR", "yf": "PLTR", "categoria": "Internacional"},
        "Netflix (NFLX)": {"tv": "NASDAQ:NFLX", "yf": "NFLX", "categoria": "Internacional"},
        "Block / Square (SQ)": {"tv": "NYSE:SQ", "yf": "SQ", "categoria": "Internacional"},
        "ADP": {"tv": "NASDAQ:ADP", "yf": "ADP", "categoria": "Internacional"},
        "ServiceNow (NOW)": {"tv": "NYSE:NOW", "yf": "NOW", "categoria": "Internacional"},
        "Globant (GLOB)": {"tv": "NYSE:GLOB", "yf": "GLOB", "categoria": "Internacional"},
        "SAP SE": {"tv": "NYSE:SAP", "yf": "SAP", "categoria": "Internacional"},
        "Palo Alto Networks (PANW)": {"tv": "NASDAQ:PANW", "yf": "PANW", "categoria": "Internacional"},
        "CrowdStrike (CRWD)": {"tv": "NASDAQ:CRWD", "yf": "CRWD", "categoria": "Internacional"},
        "Iris Energy (IREN)": {"tv": "NASDAQ:IREN", "yf": "IREN", "categoria": "Internacional"},
        "General Electric (GE)": {"tv": "NYSE:GE", "yf": "GE", "categoria": "Internacional"},
        "Berkshire Hathaway (BRK.B)": {"tv": "NYSE:BRK.B", "yf": "BRK-B", "categoria": "Internacional"},
        "Goldman Sachs (GS)": {"tv": "NYSE:GS", "yf": "GS", "categoria": "Internacional"},
        "JPMorgan Chase (JPM)": {"tv": "NYSE:JPM", "yf": "JPM", "categoria": "Internacional"},
        "Robinhood (HOOD)": {"tv": "NASDAQ:HOOD", "yf": "HOOD", "categoria": "Internacional"},
        "Visa (V)": {"tv": "NYSE:V", "yf": "V", "categoria": "Internacional"},
        "Mastercard (MA)": {"tv": "NYSE:MA", "yf": "MA", "categoria": "Internacional"},
        "MercadoLibre (MELI)": {"tv": "NASDAQ:MELI", "yf": "MELI", "categoria": "Internacional"},
        "Walmart (WMT)": {"tv": "NYSE:WMT", "yf": "WMT", "categoria": "Internacional"},
        "Target (TGT)": {"tv": "NYSE:TGT", "yf": "TGT", "categoria": "Internacional"},
        "Caterpillar (CAT)": {"tv": "NYSE:CAT", "yf": "CAT", "categoria": "Internacional"},
        "AST SpaceMobile (ASTS)": {"tv": "NASDAQ:ASTS", "yf": "ASTS", "categoria": "Internacional"},
        "Ondas Holdings (ONDS)": {"tv": "NASDAQ:ONDS", "yf": "ONDS", "categoria": "Internacional"},
        "Arista Networks (ANET)": {"tv": "NYSE:ANET", "yf": "ANET", "categoria": "Internacional"},
        "Corning (GLW)": {"tv": "NYSE:GLW", "yf": "GLW", "categoria": "Internacional"},
        "iShares Bitcoin Trust (IBIT)": {"tv": "NASDAQ:IBIT", "yf": "IBIT", "categoria": "Internacional"},
        "MicroStrategy (MSTR)": {"tv": "NASDAQ:MSTR", "yf": "MSTR", "categoria": "Internacional"},
        "Coinbase (COIN)": {"tv": "NASDAQ:COIN", "yf": "COIN", "categoria": "Internacional"},
        "Riot Platforms (RIOT)": {"tv": "NASDAQ:RIOT", "yf": "RIOT", "categoria": "Internacional"},
        "Hut 8 Mining (HUT)": {"tv": "NASDAQ:HUT", "yf": "HUT", "categoria": "Internacional"},
        "Eli Lilly (LLY)": {"tv": "NYSE:LLY", "yf": "LLY", "categoria": "Internacional"},
        "Novo Nordisk (NVO)": {"tv": "NYSE:NVO", "yf": "NVO", "categoria": "Internacional"},
        "American Airlines (AAL)": {"tv": "NASDAQ:AAL", "yf": "AAL", "categoria": "Internacional"},
        "Uber (UBER)": {"tv": "NYSE:UBER", "yf": "UBER", "categoria": "Internacional"},
        "SPDR Gold Shares (GLD)": {"tv": "AMEX:GLD", "yf": "GLD", "categoria": "Internacional"},
        "iShares Silver Trust (SLV)": {"tv": "AMEX:SLV", "yf": "SLV", "categoria": "Internacional"},
        "Global X Copper Miners (COPX)": {"tv": "NYSEARCA:COPX", "yf": "COPX", "categoria": "Internacional"},
        "Bitcoin / USDT": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD", "categoria": "Internacional"},
        "Ethereum / USDT": {"tv": "BINANCE:ETHUSDT", "yf": "ETH-USD", "categoria": "Internacional"},

        # --- MERCADO ARGENTINO (BCBA) ---
        "Índice Merval": {"tv": "BCBA:IMV", "yf": "^MERV", "categoria": "Mercado Argentino"},
        "YPF S.A. (YPFD)": {"tv": "BCBA:YPFD", "yf": "YPFD.BA", "categoria": "Mercado Argentino"},
        "Pampa Energía (PAMP)": {"tv": "BCBA:PAMP", "yf": "PAMP.BA", "categoria": "Mercado Argentino"},
        "Grupo Supervielle (SUPV)": {"tv": "BCBA:SUPV", "yf": "SUPV.BA", "categoria": "Mercado Argentino"},
        "Grupo Financiero Galicia (GGAL)": {"tv": "BCBA:GGAL", "yf": "GGAL.BA", "categoria": "Mercado Argentino"},
        "Banco Macro (BMA)": {"tv": "BCBA:BMA", "yf": "BMA.BA", "categoria": "Mercado Argentino"},
        "BBVA Argentina (BBAR)": {"tv": "BCBA:BBAR", "yf": "BBAR.BA", "categoria": "Mercado Argentino"},
        "Central Puerto (CEPU)": {"tv": "BCBA:CEPU", "yf": "CEPU.BA", "categoria": "Mercado Argentino"},
        "Transportadora de Gas del Sur (TGSU2)": {"tv": "BCBA:TGSU2", "yf": "TGSU2.BA", "categoria": "Mercado Argentino"},
        "Ternium Argentina (TXAR)": {"tv": "BCBA:TXAR", "yf": "TXAR.BA", "categoria": "Mercado Argentino"},
        "Aluar (ALUA)": {"tv": "BCBA:ALUA", "yf": "ALUA.BA", "categoria": "Mercado Argentino"},
        "Loma Negra (LOMA)": {"tv": "BCBA:LOMA", "yf": "LOMA.BA", "categoria": "Mercado Argentino"},
        "Sociedad Comercial del Plata (COME)": {"tv": "BCBA:COME", "yf": "COME.BA", "categoria": "Mercado Argentino"},
        "Transener (TRAN)": {"tv": "BCBA:TRAN", "yf": "TRAN.BA", "categoria": "Mercado Argentino"},
        "Cresud (CRES)": {"tv": "BCBA:CRES", "yf": "CRES.BA", "categoria": "Mercado Argentino"}
    }

# ==========================================
# SECCIÓN 1: CONFIGURACIÓN Y GESTIÓN DE ACTIVOS
# ==========================================
st.sidebar.header("⚙️ Configuración del Activo")

activos_disponibles = st.session_state.activos_dict

# Filtro por Categoría / Sector
filtrar_cat = st.sidebar.checkbox("Filtrar por Categoría / Sector", value=False)

if filtrar_cat:
    categorias_unicas = sorted(list(set(v["categoria"] for v in activos_disponibles.values())))
    cat_sel = st.sidebar.selectbox("Seleccionar Categoría:", categorias_unicas)
    activos_filtrados = {k: v for k, v in activos_disponibles.items() if v["categoria"] == cat_sel}
else:
    activos_filtrados = activos_disponibles

lista_opciones = [f"[{v['categoria']}] {k}" if not filtrar_cat else k for k, v in activos_filtrados.items()]
opcion_seleccionada = st.sidebar.selectbox("Seleccionar Activo:", lista_opciones)

nombre_limpio = opcion_seleccionada.split("] ")[-1] if "]" in opcion_seleccionada else opcion_seleccionada
tv_symbol = activos_disponibles[nombre_limpio]["tv"]
yf_symbol = activos_disponibles[nombre_limpio]["yf"]

# Agregar / Eliminar Activos
with st.sidebar.expander("➕ / ➖ Gestionar Lista de Activos", expanded=False):
    tab_add, tab_del = st.tabs(["Agregar Activo", "Eliminar Activo"])
    
    with tab_add:
        new_name = st.text_input("Nombre / Ticker Visible:", placeholder="Ej: Meta (META)")
        new_tv = st.text_input("Ticker TradingView:", placeholder="Ej: NASDAQ:META")
        new_yf = st.text_input("Ticker Yahoo Finance:", placeholder="Ej: META")
        new_cat = st.selectbox("Categoría / Sector:", ["Indices", "Sectores", "Internacional", "Mercado Argentino", "Otros"])
        
        if st.button("Guardar Nuevo Activo"):
            if new_name.strip() and new_tv.strip() and new_yf.strip():
                st.session_state.activos_dict[new_name.strip()] = {
                    "tv": new_tv.strip().upper(),
                    "yf": new_yf.strip().upper(),
                    "categoria": new_cat
                }
                st.success(f"¡{new_name} agregado con éxito!")
                st.rerun()
            else:
                st.error("Por favor completa todos los campos requeridos.")
                
    with tab_del:
        activo_a_borrar = st.selectbox("Activo a eliminar:", list(st.session_state.activos_dict.keys()), key="del_sel")
        if st.button("Eliminar Activo Seleccionado"):
            if len(st.session_state.activos_dict) > 1:
                del st.session_state.activos_dict[activo_a_borrar]
                st.success(f"¡{activo_a_borrar} eliminado!")
                st.rerun()
            else:
                st.warning("Debes mantener al menos un activo en la lista.")

# Selector de Temporalidades
timeframe_map = {
    "1 Minuto": {"tv": "1", "yf_interval": "1m", "yf_period": "7d"},
    "2 Minutos": {"tv": "2", "yf_interval": "2m", "yf_period": "30d"},
    "5 Minutos": {"tv": "5", "yf_interval": "5m", "yf_period": "30d"},
    "15 Minutos": {"tv": "15", "yf_interval": "15m", "yf_period": "60d"},
    "30 Minutos": {"tv": "30", "yf_interval": "30m", "yf_period": "60d"},
    "1 Hora": {"tv": "60", "yf_interval": "1h", "yf_period": "730d"},
    "2 Horas": {"tv": "120", "yf_interval": "1h", "yf_period": "730d"},
    "4 Horas": {"tv": "240", "yf_interval": "1h", "yf_period": "730d"},
    "Diario (1D)": {"tv": "D", "yf_interval": "1d", "yf_period": "5y"},
    "Semanal (1W)": {"tv": "W", "yf_interval": "1wk", "yf_period": "10y"},
    "Mensual (1M)": {"tv": "M", "yf_interval": "1mo", "yf_period": "max"}
}

tf_sel = st.sidebar.selectbox("Temporalidad del Análisis:", list(timeframe_map.keys()), index=5)
tv_tf_code = timeframe_map[tf_sel]["tv"]
yf_interval = timeframe_map[tf_sel]["yf_interval"]
yf_period = timeframe_map[tf_sel]["yf_period"]

# ==========================================
# SECCIÓN 2: PARÁMETROS DEL SCORING
# ==========================================
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
        
        # Medias Móviles Exponenciales
        ma1 = close.ewm(span=m1, adjust=False).mean()
        ma2 = close.ewm(span=m2, adjust=False).mean()
        ma3 = close.ewm(span=m3, adjust=False).mean()
        ma4 = close.ewm(span=m4, adjust=False).mean()
        ma5 = close.ewm(span=m5, adjust=False).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # ATR
        tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/a_len, adjust=False).mean()
        
        # ADX
        up, down = high.diff(), -low.diff()
        plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0), index=df.index)
        minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0), index=df.index)
        tr_smooth = tr.ewm(alpha=1/adx_l, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/adx_l, adjust=False).mean() / tr_smooth)
        minus_di = 100 * (minus_dm.ewm(alpha=1/adx_l, adjust=False).mean() / tr_smooth)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/adx_l, adjust=False).mean()
        
        # Bandas de Bollinger y MACD
        bb_basis = close.rolling(window=20).mean()
        bb_dev = 2.0 * close.rolling(window=20).std()
        bb_upper, bb_lower = bb_basis + bb_dev, bb_basis - bb_dev
        macd_line = close.ewm(span=8, adjust=False).mean() - close.ewm(span=m2, adjust=False).mean()
        signal_line = macd_line.ewm(span=14, adjust=False).mean()
        
        # SuperTrend
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
        bbm_l = float(bb_basis.iloc[-1])
        
        # SCORING DINÁMICO COMPLETO
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

res = calcular_matriz_pine(
    yf_symbol, yf_interval, yf_period,
    len_mm1, len_mm2, len_mm3, len_mm4, len_mm5,
    atr_len, atr_mult_sl, adx_len, adx_th, rsi_ob_limit, rsi_os_limit,
    st_period, st_mult, use_oracle, use_st
)

# ==========================================
# RENDER DEL GRÁFICO OFICIAL TRADINGVIEW
# ==========================================
template_tv = """
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart" style="height:550px;width:100%"></div>
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
components.html(tradingview_html, height=560)

st.markdown("---")

# ==========================================
# RENDER DE LA TABLA MATRICIAL DE 6 COLUMNAS
# ==========================================
st.subheader(f"📑 Tabla Matricial del Sistema de Trading ({tf_sel})")

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
else:
    st.warning("No hay suficientes datos disponibles para este activo en la temporalidad seleccionada.")
