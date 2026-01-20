import streamlit as st
import pandas as pd
import yfinance as yf

# -------------------------------------------------
# Streamlit Ayarları
# -------------------------------------------------
st.set_page_config(
    page_title="BIST EMA 9 / EMA 21 Tarayıcı",
    layout="wide"
)

st.title("BIST EMA(9) / EMA(21) Yukarı Kesişim Tarayıcı")
st.caption("Veri kaynağı: Yahoo Finance")

# -------------------------------------------------
# Timeframe Seçimi
# -------------------------------------------------
TIMEFRAME_OPTIONS = {
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "4 Saat": "4h",
    "1 Gün": "1d",
}

selected_label = st.selectbox(
    "Zaman Dilimi",
    list(TIMEFRAME_OPTIONS.keys()),
    index=1
)

TIMEFRAME = TIMEFRAME_OPTIONS[selected_label]

# -------------------------------------------------
# BIST Hisse Listesi (Excel)
# -------------------------------------------------
@st.cache_data
def load_symbols():
    df = pd.read_excel("hisse_kodu.xlsx")
    return df["hisse_kodu"].dropna().unique().tolist()

symbols = load_symbols()

# -------------------------------------------------
# EMA Kesişim Kontrolü
# -------------------------------------------------
def ema_crossover(df):
    df["ema9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["Close"].ewm(span=21, adjust=False).mean()

    prev = df.iloc[-2]
    last = df.iloc[-1]

    return prev["ema9"] < prev["ema21"] and last["ema9"] > last["ema21"]

# -------------------------------------------------
# Tarama
# -------------------------------------------------
results = []

with st.spinner("BIST hisseleri taranıyor..."):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            df = ticker.history(period="3mo", interval=TIMEFRAME)

            if df.empty or len(df) < 21:
                continue

            if ema_crossover(df):
                results.append({
                    "Hisse": symbol,
                    "Timeframe": TIMEFRAME
                })

        except Exception:
            continue

# -------------------------------------------------
# Sonuçlar
# -------------------------------------------------
st.subheader("Tespit Edilen Hisseler")

if results:
    st.dataframe(
        pd.DataFrame(results),
        use_container_width=True
    )
else:
    st.warning("Seçilen timeframe için EMA(9) yukarı kesişimi bulunamadı.")
