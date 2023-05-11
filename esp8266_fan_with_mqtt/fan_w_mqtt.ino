
#include <ESP8266WiFi.h>	//Use <WiFi.h> For ESP32
#include <PubSubClient.h>

// forward declarations
void setup_wifi();
void callback(String topic, byte* message, unsigned int length);
void reconnect();

// WIFI
const char* ssid = "SSID";
const char* passphrase = "password";

// MQTT
const char* mqtt_server = "mqtt.example.com"; // or ip
const int mqtt_port = 1883;
const char* mqtt_user = "prototype";
const char* mqtt_password = "password";
const char* mqtt_client_name = "client_name_random_24343234";  // must be unique

// define MQQT-Topics
const char* topic_sub = "prototype/moin_sub";
const char* topic_pub = "prototype/moin_pub";

// for millis
const int pub_interval = 10000;  // time in ms

WiFiClient wifi;
PubSubClient client(wifi);

long now;  // current uptime
long last = 0;  // uptime of last publish
int pub_counter = 0;  // Zählwert als Inhalt für eigene Publish-Nachrichten


void setup() 
{
  // Serial
  Serial.begin(9600);
  Serial.println();
  delay(100);
  Serial.println("Setup...");

  // WiFi
  setup_wifi();

  // start MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  Serial.println("Success c(o_o)c ");
}

void loop() 
{

  int tempValue = analogRead(A0);
  int TempF = map(tempValue, 0, 410, -50, 150);
  int TempC = (TempF-32)*.5556;
  
  Serial.println(TempC);
  Serial.println();
  delay(1000);

  char val[10]; 
  dtostrf(TempC, 4, 2, val); // map stuff into val

  // TempC = the value that we are converting 
  // 4 = are the number of digits
  // 2 = are the number of decimals
  // val = return value
  

  if (!client.connected())
  {
    reconnect();
  }

  client.loop(); // ??

  now = millis();
  if (millis() - last > pub_interval)
  {
    last = now;
    pub_counter++;
    client.publish(topic_pub, val );
    Serial.print("Publish: ");
    Serial.print(topic_pub);
    Serial.print(": ");
    Serial.println(pub_counter);

    
        if ( TempC > 30 ){
          Serial.println("Fan running");
            
          digitalWrite(D0, HIGH);
          delay(5000); // Wait for 5000 millisecond(s)
        
          digitalWrite(D0, LOW);
          delay(5000); // Wait for 5000 millisecond(s)
       
        }
        else if ( TempC < 30 ){
          digitalWrite(D0, LOW);
          Serial.println("Fan not running");
          delay(1000);
          
        }
    
  }
}


void setup_wifi()
{
  delay(10);
  Serial.print("WiFi");
  WiFi.begin(ssid, passphrase);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }
  Serial.println(" connected");
}

// callback
void callback(String topic, byte* message, unsigned int length)
{

  String messageTemp;
  
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);

  for (int i = 0; i < length; i++) 
  {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  if (topic == topic_sub) 
  {
    if (messageTemp == "on")
    {
      Serial.print(topic_sub);
      Serial.println(" turn on message recieved, turning on for 5 seconds");
      digitalWrite(D0, HIGH); // turn on
      delay(5000); // wait 5000 ms
      digitalWrite(D0, LOW); // turn off
    }
    else if (messageTemp == "off")
    {
      Serial.print(topic_sub);
      Serial.println(" turn off message recieved, turning off");
      digitalWrite(D0, LOW); // turn off
      delay(5000); // wait 5000 ms
    }
  }

}


void reconnect() //
{
  while (!client.connected())
  {
    Serial.println("MQTT reconnect");
    if (client.connect(mqtt_client_name, mqtt_user, mqtt_password))
    {
      Serial.println("connected to MQTT server");
      client.subscribe(topic_sub);
    }
    else
    {
      Serial.print("MQTT connection failed: ");
      Serial.println(client.state());
      delay(5000);
    }
  }
}
