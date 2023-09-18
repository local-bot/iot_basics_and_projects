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
MQTT_BROKER = "your_ip_here"
CLIENT_ID = 'wtf_is_an_client_id'
publish_topic_moisture_porcentage = b'/watering/pico/moisture'
publish_topic_sensor_value = b'/watering/pico/sensor'
publish_topic_water_pump_status = b'/watering/pico/water_pump_status'

def mqtt_connect():
    global mqttClient
    print(f"Begin connection with MQTT Broker: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, user="mqtt-bot", password="Pizza_Password", keepalive=3600)
    mqttClient.connect()
    print(f'Connected to {MQTT_BROKER} MQTT Broker')

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

def read_moisture():
    adc_value = soil_pin.read_u16()
    moisture = 100 - ((adc_value - wet_value) * 100 / (dry_value - wet_value))

    # print(f"Moisture: {moisture:.2f}% | ADC Value: {adc_value}")
    mqttClient.publish(publish_topic_moisture_porcentage, str(f"{moisture:.2f}%"))
    mqttClient.publish(publish_topic_sensor_value, str(adc_value))

    return moisture, adc_value

def control_relays():
    moisture, adc_value = read_moisture()

    if moisture < 60:
        relay_pin.value(1)
        # print(f"water pump turned on, watering for 5 seconds | Relay value: {relay_pin.value()} | Moisture: {moisture} ")
        mqttClient.publish(publish_topic_water_pump_status, b'Water pump turned on 5 seconds')
        green_led(1)
        red_led(1)
        time.sleep(5)

        relay_pin.value(0)
        # print(f"water pump turned off again | Relay value: {relay_pin.value()}")
        mqttClient.publish(publish_topic_water_pump_status, b'Water pump turned off again, sleeping 5 hours')
        red_led(0)
        time.sleep(3600) # 3600 | 1 hour sleep after watering

    else:
        red_led(0)
        green_led(1)
        relay_pin.value(0)
        mqttClient.publish(publish_topic_water_pump_status, f"Moisture {moisture:.2f}%, next check in 4 hours")

mqtt_connect() # Connect to MQTT broker before loop

while True:
    control_relays()
    time.sleep(14400) # 14400 | 4 hours sleep before next check
