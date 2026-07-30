import network
import espnow
import select
import time
import os
from machine import Pin, I2C, SDCard
import sh1106

# --- Configuración del I2C y OLED SH1106 ---
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = sh1106.SH1106_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Receptor listo", 0, 0)
oled.text("Esperando msg...", 0, 16)
oled.show()

# --- Configuración de ESP-NOW ---
sta = network.WLAN(network.WLAN.IF_STA)
sta.active(True)

e = espnow.ESPNow()
e.active(True)  

print("Receptor listo. Esperando mensajes por HT-0000...\n")

poll = select.poll()
poll.register(e, select.POLLIN)

ultimo_msg = None  # timestamp del último mensaje
fecha = "--/--/--"
hora = "--:--"
valor = "0"

while True:
    events = poll.poll(1000) 
    if events:
        try:
            mac, msg = e.irecv(0) 
            if mac:
                # Guardar tiempo del último mensaje
                ultimo_msg = time.time()
                print("Mensaje recibido. Guardando timestamp...")
                
                # Convertir a string
                linea_str = msg.decode('utf-8').strip()
                
                # Separar por comas
                valores = linea_str.split(',')
                if len(valores) >=3:
                    nombre = valores[0]
                    fecha = valores[1]
                    hora = valores[2]
                    valor = valores[3]
                    print("Valores extraídos:", valores)
                    
                    # Intentar guardar en la tarjeta SD
                    try:
                        sd = SDCard(slot=2, cs=Pin(26), sck=Pin(18), mosi=Pin(23), miso=Pin(19), freq=1000000)
                        os.mount(sd, '/sd')
                        with open('/sd/registro.txt', 'a') as f:
                            f.write(linea_str + '\n')
                            print("Guardado en SD")
                        os.umount('/sd')
                    except Exception as err_sd:
                        print('Error detallado al usar la SD:', err_sd)
                else:
                    print("Formato de mensaje incorrecto", linea_str)
        except Exception as err:
            print('Error en recepción HT-0000:', err)
            
    # --- Mostrar en OLED cada ciclo ---
    oled.fill(0)
    if ultimo_msg is None:
        oled.text("HT-0000", 0, 0)
        oled.text("Sin mensajes", 0, 20)
    else:
        oled.text("HT-0000", 0, 0)
        oled.text("Hora:" + hora, 0, 10)
        oled.text("Inf de:" + nombre, 0, 25)
        oled.text("Fecha:" + fecha, 0, 40)
        oled.text("Ult Valor:" + valor, 0, 55)
    oled.show()
