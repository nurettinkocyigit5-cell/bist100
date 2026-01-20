import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide")
st.title("BIST EMA(9/21) Tarayıcı (Google Finance Kaynağına Yakın)")

# -------------------------------------------------
# Timeframe
# -------------------------------------------------
INTERVAL = st.selectbox(
    "Zaman Dilimi",
    ["1h", "1d"],
    index=1
)

# -------------------------------------------------
# BIST Listesi
# -------------------------------------------------
@st.cache
def get_bist_tickers():
    url = "https://raw.githubusercontent.com/datasets/borsa-istanbul/master/data/bist100-listed-companies.csv"
    df = pd.read_csv(url)
    return [f"{sym}.IS" for sym in df["Ticker"]]

symbols = get_bist_tickers()

# -------------------------------------------------
# EMA Fonksiyonu
# -------------------------------------------------
def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval=INTERVAL, progress=False)
        if df.empty:
            return None
        return df
    except:
        return None

def ema_crossover(df):
    df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()

    if len(df) < 22:
        return False

    prev = df.iloc[-2]
    last = df.iloc[-1]
    return prev["EMA9"] < prev["EMA21"] and last["EMA9"] > last["EMA21"]

# -------------------------------------------------
# Tarama
# -------------------------------------------------
results = []

with st.spinner("BIST hisseleri taranıyor..."):
    for symbol in symbols:
        df = fetch_data(symbol)
        if df is None:
            continue
        if ema_crossover(df):
            results.append({
                "Hisse": symbol.replace(".IS", ""),
                "Son Fiyat": round(df["Close"].iloc[-1], 2),
                "Zaman Dilimi": INTERVAL
            })

# -------------------------------------------------
# Sonuçlar
# -------------------------------------------------
if results:
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.warning("EMA(9/21) yukarı kesişimi yapan BIST hissesi bulunamadı.")
