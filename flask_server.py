from flask import Flask, jsonify
from opcua import Client
import pandas as pd
import logging

app = Flask(__name__)

# === Loglama Ayarları ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === OPC-UA Veri Çekme Fonksiyonu ===
def oku_opc_verileri():
    try:
        client = Client("opc.tcp://localhost:4840/")
        client.connect()
        logger.info("OPC-UA bağlantısı başarılı.")

        uretim = client.get_node("ns=2;s=SoftPLC.UretimSayisi").get_value()
        stok = client.get_node("ns=2;s=SoftPLC.StokSeviyesi").get_value()
        client.disconnect()
        logger.info(f"OPC Verileri → Üretim: {uretim}, Stok: {stok}")
        return {"uretim": uretim, "stok": stok}
    except Exception as e:
        logger.error(f"OPC-UA bağlantı hatası: {e}")
        return {"hata": "OPC bağlantısı başarısız"}

# === Route: /veri → Canlı OPC-UA verisi döner
@app.route("/veri")
def veri_al():
    veriler = oku_opc_verileri()
    return jsonify(veriler)

# === Route: /log → log.csv içeriğini JSON olarak döner
@app.route("/log")
def log_al():
    try:
        df = pd.read_csv("log.csv")
        return df.to_json(orient="records")
    except FileNotFoundError:
        logger.warning("log.csv dosyası bulunamadı.")
        return jsonify({"hata": "log.csv dosyası bulunamadı"})
    except Exception as e:
        logger.error(f"Log verisi okunamadı: {e}")
        return jsonify({"hata": "Log verisi okunamadı"})

# === Sunucuyu Başlat
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
