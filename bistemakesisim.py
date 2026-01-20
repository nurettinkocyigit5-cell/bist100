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

st.title("BIST EMA(9) / EMA(21) Yukarı Kesişim Tarayıcı")

# -------------------------------------------------
# Timeframe Seçimi
# -------------------------------------------------
TIMEFRAMES = {
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "4 Saat": "4h",
    "1 Gün": "1d",
}

tf_label = st.selectbox(
    "Zaman Dilimi",
    list(TIMEFRAMES.keys()),
    index=1
)

TIMEFRAME = TIMEFRAMES[tf_label]

# -------------------------------------------------
# Hisse Listesi (Excel - TAM DOSYA YOLU)
# -------------------------------------------------
EXCEL_PATH = r"C:\Users\ASUS\OneDrive\Desktop\bist\hisse_kodu.xlsx"

df_symbols = pd.read_excel(EXCEL_PATH)

# Excel sütun adı: hisse_kodu
symbols = (df_symbols["hisse_kodu"].astype(str) + ".IS").tolist()

# -------------------------------------------------
# EMA Kesişim Fonksiyonu
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

if st.button("Taramayı Başlat"):
    with st.spinner("BIST hisseleri taranıyor..."):
        for symbol in symbols:
            try:
                df = yf.download(
                    symbol,
                    period="3mo",
                    interval=TIMEFRAME,
                    progress=False
                )

                if df is not None and len(df) >= 21:
                    if ema_crossover(df):
                        results.append(symbol)

            except Exception:
                pass

    # -------------------------------------------------
    # Sonuçlar
    # -------------------------------------------------
    if results:
        st.success(f"{len(results)} hisse bulundu")
        st.dataframe(
            pd.DataFrame(results, columns=["Hisse"]),
            use_container_width=True
        )
    else:
        st.warning("Şartları sağlayan hisse bulunamadı.")
