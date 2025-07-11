import streamlit as st
import time
import pandas as pd
from datetime import datetime
from opcua import Client

# === Dosya ve Sayfa Ayarları ===
log_dosyasi = "log.csv"
if not pd.io.common.file_exists(log_dosyasi):
    pd.DataFrame(columns=["Zaman", "Üretim", "Stok"]).to_csv(log_dosyasi, index=False)

st.set_page_config(page_title="ERP Dashboard", layout="centered")
st.title("ERP Paneli – Canlı Takip + Loglama + Raporlama")

# === OPC-UA Bağlantısı ===
try:
    client = Client("opc.tcp://localhost:4840/")
    client.connect()
    connected = True
    st.success("OPC-UA bağlantısı başarılı.")
except Exception as e:
    connected = False
    st.error("OPC-UA bağlantısı başarısız.")
    st.exception(e)

# === Veri Okuma Fonksiyonu ===
def oku_veriler():
    try:
        uretim = client.get_node("ns=2;s=SoftPLC.UretimSayisi")
        stok = client.get_node("ns=2;s=SoftPLC.StokSeviyesi")
        return uretim.get_value(), stok.get_value()
    except:
        return None, None

# === Uygulama ===
if connected:
    metric_placeholder = st.empty()
    chart_placeholder = st.empty()
    table_placeholder = st.empty()

    try:
        while True:
            # Canlı veri çek
            uretim_sayisi, stok_miktari = oku_veriler()

            if uretim_sayisi is None:
                st.error("OPC-UA verisi alınamadı.")
                break

            # CSV'ye yaz
            yeni_kayit = pd.DataFrame({
                "Zaman": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "Üretim": [uretim_sayisi],
                "Stok": [stok_miktari]
            })
            yeni_kayit.to_csv(log_dosyasi, mode='a', header=False, index=False)

            # CSV'den oku
            df = pd.read_csv(log_dosyasi)
            df["Zaman"] = pd.to_datetime(df["Zaman"])

            # Metin ve Uyarı Göstergeleri
            with metric_placeholder.container():
                st.subheader("Canlı Veriler")
                st.metric("Üretim Sayısı", uretim_sayisi)
                st.metric("Kalan Stok", stok_miktari)

                if stok_miktari == 0:
                    st.error("Stok tükendi! Üretim durmalı.")
                elif stok_miktari <= 2:
                    st.warning("Stok azaldı! Yeni sipariş verilmeli.")

                st.caption("Veriler her 2 saniyede bir güncellenir.")

            # Grafik
            with chart_placeholder.container():
                st.subheader("Zaman Serisi")
                st.line_chart(df.set_index("Zaman")[["Üretim", "Stok"]])

            # Son Kayıtlar + Raporlama
            with table_placeholder.container():
                st.subheader("Log Verisi – Son 10 Kayıt")
                st.dataframe(df.tail(10).sort_values(by="Zaman", ascending=False), use_container_width=True)

                with st.expander("Raporlama ve CSV İndir"):
                    df = pd.read_csv(log_dosyasi)
                    df["Zaman"] = pd.to_datetime(df["Zaman"])

                    start_date = st.sidebar.date_input(
                        "Başlangıç Tarihi",
                        value=df["Zaman"].min().date(),
                        key="unique_start"
                    )
                    end_date = st.sidebar.date_input(
                        "Bitiş Tarihi",
                        value=df["Zaman"].max().date(),
                        key="unique_end"
                    )

                    filtreli = df[(df["Zaman"].dt.date >= start_date) & (df["Zaman"].dt.date <= end_date)]

                    st.write(f"Seçilen tarihler arasında {len(filtreli)} kayıt bulundu.")
                    st.dataframe(filtreli, use_container_width=True)

                    ort_uretim = filtreli["Üretim"].mean()
                    ort_stok = filtreli["Stok"].mean()

                    st.info(f"Günlük Ortalama Üretim: {ort_uretim:.2f} | Ortalama Stok: {ort_stok:.2f}")

                    csv = filtreli.to_csv(index=False).encode("utf-8")
                    st.download_button("CSV'yi İndir", csv, file_name="rapor.csv", mime="text/csv")

            time.sleep(2)

    except Exception as e:
        st.error("Uygulama hatası oluştu.")
        st.exception(e)

    finally:
        client.disconnect()
        st.success("OPC-UA bağlantısı kapatıldı.")
