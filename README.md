# Industrial Mini ERP & SCADA Simulation Panel

Donanımsız, Gerçek Zamanlı, Açık Kaynaklı PLC–SCADA–ERP Simülasyonu  
Python + Flutter + OPC-UA + MQTT + REST + Web & Mobil Panel

---

## Proje Özeti

Bu proje, üretim takibi, stok yönetimi, veri kaydı ve görselleştirme ihtiyaçlarını karşılamak için geliştirilmiş tam entegre bir ERP & SCADA simülasyon panelidir.  
Donanımsız olarak çalışır; **OPC-UA**, **MQTT**, **REST API**, **Streamlit**, **Flutter** gibi modern teknolojilerle geliştirilmiştir.

---

## Sistem Mimarisi

```text
[main.py] (SoftPLC üretim simülasyonu)
       │
OPC-UA & MQTT
       │
[opcua_server.py]       [flask_server.py]
       │                        │
[erp_dashboard.py]    [Flutter Panel (main.dart)]
       │                        │
  Web Panel            Mobil/Web Panel
       │________________________│
           [log.csv] (veri kaydı)
