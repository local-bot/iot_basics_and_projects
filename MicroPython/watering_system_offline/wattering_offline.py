from machine import ADC, Pin
import utime

soil_pin = ADC(Pin(26))
relay_pin = Pin(16, Pin.OUT)
dry_value = 59000
wet_value = 24500

def read_moisture():
    adc_value = soil_pin.read_u16()
    moisture = 100 - ((adc_value - wet_value) * 100 / (dry_value - wet_value))
    return moisture, adc_value

def my_relay(moisture):
    if moisture < 60:
        relay_pin.value(0)
        print(f"moisture unde 60% {relay_pin.value()}, wattering for 5 seconds")
        utime.sleep(5)
        relay_pin.value(1)
        print(f"turning pump off again {relay_pin.value()}")
    else:
        print(f"moisture ok {relay_pin.value()}, sleeping 5 seconds")
        relay_pin.value(1)
        utime.sleep(5)

while True:
    moisture, adc_value = read_moisture()
    print(f"Moisture: {moisture:.2f}% | ADC Value: {adc_value}")
    my_relay(moisture)
    utime.sleep(1)
