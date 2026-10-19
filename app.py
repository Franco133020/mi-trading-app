import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="Mi TradingView Personal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #161922; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Mi Plataforma de Análisis Técnico")

# Sidebar - Panel de Control
st.sidebar.header("⚙️ Configuración del Gráfico")

# Lista de activos sugeridos y entrada personalizada
categorias = {
    "Acciones EE.UU.": ["NASDAQ:AAPL", "NASDAQ:NVDA", "NASDAQ:TSLA", "NASDAQ:MSFT", "NYSE:AMZN"],
    "Criptomonedas": ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"],
    "CEDEARs / Argentina": ["BCBA:GGAL", "BCBA:YPFD", "BCBA:PAMP", "BCBA:MELI"]
}

categoria_sel = st.sidebar.selectbox("Seleccionar Categoría:", list(categorias.keys()))
activo_sugerido = st.sidebar.selectbox("Activo:", categorias[categoria_sel])

simbolo_personalizado = st.sidebar.text_input("O ingresar Ticker manual (Ej: NASDAQ:GOOGL):", value=activo_sugerido)
simbolo_final = simbolo_personalizado.strip().upper() if simbolo_personalizado else activo_sugerido

# Selección de Intervalo / Temporalidad
intervalos = {
    "1 Minuto": "1",
    "5 Minutos": "5",
    "15 Minutos": "15",
    "1 Hora": "60",
    "Diario": "D",
    "Semanal": "W"
}
intervalo_sel = st.sidebar.selectbox("Temporalidad:", list(intervalos.keys()), index=4)
intervalo_codigo = intervalos[intervalo_sel]

# Renderizado del Widget de TradingView
st.markdown(f"### Cotización en Tiempo Real: `{simbolo_final}`")

tradingview_html = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart" style="height:650px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true,
      "symbol": "{simbolo_final}",
      "interval": "{intervalo_codigo}",
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

# Cargar el gráfico en el contenedor principal de Streamlit
components.html(tradingview_html, height=670)