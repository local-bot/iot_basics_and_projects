import network
from machine import ADC
import time
import utime
from machine import Pin
from umqtt.simple import MQTTClient

soil = ADC(Pin(27))
led = Pin("LED", Pin.OUT)
relay = Pin(0, Pin.OUT)

when_wet = 24300
when_dry = 58398

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("wireless_AP","Piza123!:)") # safe password :)
time.sleep(5)
print(wlan.isconnected())


mqtt_server = '192.168.2.2'
client_id = 'wtf_is_an_client_id' # no idea what this does
topic_pub = b'/wattering/pico'
topic_pub_2 = b'/wattering/pico/info'

#topic_msg = b'something happened' 

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user="mqqt-bot", password="Pizza123!:)", keepalive=3600) # using safe password again :)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

try:
    client = mqtt_connect()
except OSError as e:
    reconnect()
    
    
def get_moisture():
    utime.sleep(5)
    moisture_sensor =  (when_dry-soil.read_u16())*100/(when_dry-when_wet)
    return moisture_sensor
  
def control_relays():
    moisture = get_moisture()
    print("Bodenfeuchtigkeit liegt bei " + "%.2f" % moisture +"% (ADC Wert: "+str(soil.read_u16())+")")
    topic_msg = b"%.2f" % moisture
    client.publish(topic_pub, topic_msg)
    
    if moisture < 60:
        client.publish(topic_pub_2, b'Wasserpumpe läuft gerade')
        led.value(1)        
        relay.value(0)
        utime.sleep(5)
        
        led.value(0)
        relay.value(1)
    else:
        led.value(0)
        relay.value(1)


while True:
    relay.value(0)
    control_relays()
    