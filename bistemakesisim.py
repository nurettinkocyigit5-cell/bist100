import streamlit as st
import pandas as pd
import yfinance as yf

# -------------------------------------------------
# Streamlit Ayarları
# -------------------------------------------------
st.set_page_config(
    page_title="BIST EMA 9 / EMA 21 (1D)",
    layout="wide"
)

st.title("BIST EMA(9) / EMA(21) Tarayıcı – Günlük")
st.caption("Sadece kapanmış günlük mumlar | Veri: Yahoo Finance")

TIMEFRAME = "1d"

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
    prev = df.iloc[-3]   # önceki kapanış
    last = df.iloc[-2]   # son kapanış
    return prev["ema9"] < prev["ema21"] and last["ema9"] > last["ema21"]

def is_ema9_above_ema21(df):
    last = df.iloc[-2]
    return last["ema9"] > last["ema21"]

# -------------------------------------------------
# Tarama
# -------------------------------------------------
crossover_results = []
trend_results = []

with st.spinner("BIST hisseleri taranıyor (1D)..."):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            df = ticker.history(period="1y", interval=TIMEFRAME)

            if df.empty or len(df) < 30:
                continue

            df = calculate_ema(df)
            last = df.iloc[-2]

            if is_crossover(df):
                crossover_results.append({
                    "Hisse": symbol,
                    "EMA9": round(last["ema9"], 2),
                    "EMA21": round(last["ema21"], 2)
                })

            if is_ema9_above_ema21(df):
                trend_results.append({
                    "Hisse": symbol,
                    "EMA9": round(last["ema9"], 2),
                    "EMA21": round(last["ema21"], 2)
                })

        except Exception:
            continue

# -------------------------------------------------
# Sonuçlar
# -------------------------------------------------
st.subheader("📈 EMA(9) → EMA(21) Yukarı Kesişim (Günlük)")

if crossover_results:
    st.dataframe(pd.DataFrame(crossover_results), use_container_width=True)
else:
    st.info("Yukarı kesişim bulunamadı.")

st.subheader("📊 EMA(9) > EMA(21) Olan Hisseler (Trend Devam)")

if trend_results:
    st.dataframe(pd.DataFrame(trend_results), use_container_width=True)
else:
    st.info("EMA(9), EMA(21)'in üzerinde olan hisse bulunamadı.")
