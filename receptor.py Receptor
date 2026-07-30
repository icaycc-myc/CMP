import network
import espnow
import select
import time
from machine import Pin, I2C
import sh1106

# --- Configuración del I2C y OLED SH1106 ---
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = sh1106.SH1106_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Receptor listo", 0, 0)
oled.text("Esperando msg...", 0, 16)
oled.show()

# --- Configuración de ESP-NOW ---
# WiFi
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
# Objeto ESPNOW
e = espnow.ESPNow()
e.active(True)
print("Receptor listo. Esperando mensajes por HT-0000...\n")

poll = select.poll()
poll.register(e, select.POLLIN)

while True:
    events = poll.poll(1000) 
    if events:
        try:
            mac, msg = e.irecv(0) 
            if mac:
                texto = msg.decode() if isinstance(msg, bytes) else str(msg)
                print("Recibido de", mac, "→", texto)

                # Mostrar en OLED
                oled.fill(0)
                oled.text("Recibido:", 0, 0)
                oled.text(texto[:16], 0, 20)  # Máx 16 chars por línea
                oled.show()

        except Exception as err:
            print("Error en irecv():", err)
    else:
        continue
