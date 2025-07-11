from opcua import Client

# OPC-UA sunucusuna bağlan
client = Client("opc.tcp://localhost:4840/")
client.connect()
print("OPC-UA sunucusuna bağlantı başarılı!")

try:
    # Üretim ve stok değişkenlerini al
    uretim = client.get_node("ns=2;s=SoftPLC.UretimSayisi")
    stok = client.get_node("ns=2;s=SoftPLC.StokSeviyesi")

    # Değerleri oku
    uretim_degeri = uretim.get_value()
    stok_degeri = stok.get_value()

    # Sonuçları yazdır
    print(f"Üretim Sayısı: {uretim_degeri}")
    print(f"Stok Seviyesi: {stok_degeri}")

finally:
    # Bağlantıyı kapat
    client.disconnect()
    print("Bağlantı kapatıldı.")
