from opcua import Server, ua
import time

# OPC-UA Sunucusunu oluştur
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

# Namespace tanımla
uri = "http://softplc.org"
idx = server.register_namespace(uri)

# Root > Objects > SoftPLC
objects = server.get_objects_node()
plc = objects.add_object(idx, "SoftPLC")

# Değişkenleri tanımla (string NodeId ile!)
urun_sayisi = plc.add_variable(ua.NodeId("SoftPLC.UretimSayisi", idx), "UretimSayisi", 0)
stok_seviyesi = plc.add_variable(ua.NodeId("SoftPLC.StokSeviyesi", idx), "StokSeviyesi", 100)

# Yazılabilir yap
urun_sayisi.set_writable()
stok_seviyesi.set_writable()

# Sunucuyu başlat
server.start()
print("OPC-UA Server aktif: opc.tcp://localhost:4840")

try:
    count = 0
    stok = 100
    while stok > 0:
        count += 1
        stok -= 1
        urun_sayisi.set_value(count)
        stok_seviyesi.set_value(stok)
        print(f"OPC → Üretim={count}, Stok={stok}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Sunucu durduruluyor...")

finally:
    server.stop()
    print("Sunucu kapatıldı.")
