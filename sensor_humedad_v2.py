from machine import ADC, Pin, I2C
from time import sleep
import machine
import os
sleep(3)
led = Pin(13, Pin.OUT)
led.value(1)
re=machine.reset_cause()
print(re)
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
DS3231_ADDR = 0x68
def bcd2dec(bcd):
    return((bcd >> 4) * 10 + (bcd & 0x0F))
def dec2bcd(dec):
    return (dec // 10 << 4) + (dec % 10)
def read_ds3231_time():
    data = i2c.readfrom_mem (DS3231_ADDR, 0x00,7)
    seconds = bcd2dec(data[0])
    minutes = bcd2dec(data[1])
    hours = bcd2dec(data[2])
    weekday = bcd2dec(data[3])
    day = bcd2dec(data[4])
    month = bcd2dec(data[5] & 0x1F)
    year = bcd2dec(data[6]) + 2000
    return (year, month, day, weekday, hours, minutes, seconds)
if re==5:
    print("Inicio...")
else:
    print("Despertó del modo deep sleep")
fecha_hora = read_ds3231_time()
timestamp = "{:04d}-{:02d}-{:02d},Semana:{},". format(fecha_hora[0], fecha_hora[1], fecha_hora[2], fecha_hora[3])
timestamp += "{:02d}:{:02d}:{:02d}". format(fecha_hora[4], fecha_hora[4], fecha_hora[5], fecha_hora[6])
sd = machine.SDCard(slot=2, freq=1000000)
os.mount(sd, '/sd')
adc1 = ADC(Pin(32))
adc2= ADC(Pin(12))
adc1.atten(ADC.ATTN_11DB)
adc2.atten(ADC.ATTN_11DB)

val1 = adc1.read_u16()
val2 = adc2.read_u16()
mV=val1*(2450-150)/2**16
mV2=val2*(2450-150)/2**16
V=mV/1000
V2=mV2/1000
H=2.589*10**-10*mV**4-5.010*10**-7*mV**3+3.523*10**-4*mV**2-9.135*10**-2*mV+7.457
H2=mV*(1250-300)/0.69
H22=2.589*10**-10*mV2**4-5.010*10**-7*mV2**3+3.523*10**-4*mV2**2-9.135*10**-2*mV2+7.457
r = f"{timestamp},{val1},{V:.3f},{H:.3f},{H2:.3f},{val2},{V2:.3f},{H22:.3f}\n"
with open('/sd/registro.txt', 'a') as f:
    f.write(r)
    print(r)
os.umount('/sd')
print("Entrando en modo deep sleep por 1 minuto...")
led.value(0)
machine.deepsleep(57000)