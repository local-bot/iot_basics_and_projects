import network
from machine import ADC, Pin
import time
from umqtt.simple import MQTTClient

# led and relay
green_led = Pin("LED", Pin.OUT)
red_led = Pin(27, Pin.OUT)
relay_pin = Pin(17, Pin.OUT)

# moisture
soil_pin = ADC(Pin(26))
dry_value = 62000
wet_value = 7000

# mqtt
MQTT_BROKER = "ip_of_mqtt_broker"
CLIENT_ID = 'wtf_is_an_client_id'
publish_topic_moisture_porcentage = b'/watering/pico/moisture'
publish_topic_water_pump_status = b'/watering/pico/water_pump_status'
SUBSCRIBE_TOPIC = b"/watering/pico/to_pico"

def mqtt_connect():
    global mqttClient  # Declare that we want to use the global mqttClient
    print(f"Begin connection with MQTT Broker: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, user="mqtt-bot", password="safe_password", keepalive=3600)
    mqttClient.connect()
    mqttClient.set_callback(sub_cb)  # Set the callback function
    mqttClient.subscribe(SUBSCRIBE_TOPIC)  # Subscribe to the desired topic
    print(f'Connected to {MQTT_BROKER} MQTT Broker')

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

def sub_cb(topic, msg):
    print(f"subscribed to topic: {topic} | received message : {msg}")
    if msg.decode() == "ON":
        control_relays(True)
    elif msg.decode() == "SLEEP":
        mqttClient.publish(publish_topic_water_pump_status, b'sleeping for 5 hours')
        time.sleep(18000) # 18000 | 5 Hours sleep after watering)
    else:
        control_relays(False)

def read_moisture():
    adc_value = soil_pin.read_u16()
    moisture = 100 - ((adc_value - wet_value) * 100 / (dry_value - wet_value))
    
    print(f"Moisture: {moisture:.2f}% | ADC Value: {adc_value}")
    mqttClient.publish(publish_topic_moisture_porcentage, str(f"{moisture:.2f}%"))
    # mqttClient.publish(publish_topic_water_pump_status, str(adc_value))
    
    return moisture, adc_value
  
def control_relays(on=False):
    moisture, adc_value = read_moisture()
    
    if moisture < 60 or on:
        print(f"water pump turned on, waterin for 5 seconds | Relay value: {relay_pin.value()} | Moisture: {moisture} ")
        relay_pin.value(1) 
        green_led(1)
        red_led(1)
        mqttClient.publish(publish_topic_water_pump_status, b'Water pump turned on')
        time.sleep(5)
        
        relay_pin.value(0)
        mqttClient.publish(publish_topic_water_pump_status, b'Water pump turned off again, sleeping for 5 hours')
        print(f"water pump turned off again | Relay value: {relay_pin.value()}")
        
        red_led(0)
        time.sleep(18000) # 18000 | 5 Hours sleep after watering
        
        
    else:
        red_led(0)
        green_led(0)
        relay_pin.value(0)

mqtt_connect() # Connect to MQTT broker

while True:
    control_relays()
    mqttClient.check_msg()
    time.sleep(1)

