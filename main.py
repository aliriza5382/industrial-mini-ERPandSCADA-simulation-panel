import time
import paho.mqtt.client as mqtt

class SoftPLC:
    def __init__(self):
        self.running = False
        self.product_count = 0
        self.stock = 10

        # MQTT istemcisi
        self.client = mqtt.Client()
        self.client.connect("localhost", 1883, 60)  # broker IP + port

    def start(self):
        if self.stock > 0:
            self.running = True
            print("Üretim başlatıldı.")
            self.client.publish("plc/status", "started")
        else:
            print("Stok yok!")
            self.client.publish("plc/status", "stok_tukendi")

    def stop(self):
        self.running = False
        print("Üretim durduruldu.")
        self.client.publish("plc/status", "stopped")

    def produce(self):
        if self.running:
            if self.stock > 0:
                self.product_count += 1
                self.stock -= 1
                print(f"Üretildi: {self.product_count} | Kalan: {self.stock}")
                self.client.publish("plc/urun", str(self.product_count))
                self.client.publish("plc/stok", str(self.stock))
            else:
                print("Stok tükendi!")
                self.client.publish("plc/status", "stok_tukendi")
                self.stop()

# === Başlat ===
plc = SoftPLC()
plc.start()

for _ in range(15):
    plc.produce()
    time.sleep(1)

plc.stop()
