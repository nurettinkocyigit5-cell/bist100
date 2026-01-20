import streamlit as st
import pandas as pd
import yfinance as yf

# -------------------------------------------------
# Streamlit Ayarları
# -------------------------------------------------
st.set_page_config(
    page_title="BIST EMA Tarayıcı",
    layout="wide"
)

st.title("BIST EMA(9) / EMA(21) Tarayıcı")
st.caption("Veri kaynağı: Yahoo Finance (kapanan mumlar)")

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
# BIST Hisse Listesi
# -------------------------------------------------
@st.cache_data
def load_symbols():
    df = pd.read_excel("hisse_kodu.xlsx")
    return df["hisse_kodu"].dropna().unique().tolist()

symbols = load_symbols()

# -------------------------------------------------
# EMA Hesapları
# -------------------------------------------------
def calculate_ema(df):
    df["ema9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["Close"].ewm(span=21, adjust=False).mean()
    return df

def is_crossover(df):
    prev = df.iloc[-2]
    last = df.iloc[-1]
    return prev["ema9"] < prev["ema21"] and last["ema9"] > last["ema21"]

def is_ema9_above_ema21(df):
    last = df.iloc[-1]
    return last["ema9"] > last["ema21"]

# -------------------------------------------------
# Tarama
# -------------------------------------------------
crossover_results = []
trend_results = []

with st.spinner("BIST hisseleri taranıyor..."):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            df = ticker.history(period="3mo", interval=TIMEFRAME)

            if df.empty or len(df) < 21:
                continue

            df = calculate_ema(df)

            if is_crossover(df):
                crossover_results.append({
                    "Hisse": symbol,
                    "EMA9": round(df.iloc[-1]["ema9"], 2),
                    "EMA21": round(df.iloc[-1]["ema21"], 2)
                })

            if is_ema9_above_ema21(df):
                trend_results.append({
                    "Hisse": symbol,
                    "EMA9": round(df.iloc[-1]["ema9"], 2),
                    "EMA21": round(df.iloc[-1]["ema21"], 2)
                })

        except Exception:
            continue

# -------------------------------------------------
# SONUÇLAR
# -------------------------------------------------
st.subheader("📈 EMA(9) → EMA(21) Yukarı Kesişim")

if crossover_results:
    st.dataframe(
        pd.DataFrame(crossover_results),
        use_container_width=True
    )
else:
    st.info("Yukarı kesişim bulunamadı.")

st.subheader("📊 EMA(9) > EMA(21) Olan Hisseler")

if trend_results:
    st.dataframe(
        pd.DataFrame(trend_results),
        use_container_width=True
    )
else:
    st.info("EMA(9), EMA(21)'in üzerinde olan hisse bulunamadı.")
