#!/usr/bin/python3

import time, os, random, logging, signal, sys
from paho.mqtt import client as mqtt_client
from dotenv import dotenv_values

logging.basicConfig(level=logging.DEBUG)

secrets = dotenv_values(".env")

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

broker = secrets["MQTT_BROKER"]
port = int(secrets["MQTT_PORT"])
topic = secrets["MQTT_TOPIC"]
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = secrets["MQTT_USERNAME"]
password = secrets["MQTT_PASSWORD"]

dt = 10    # time interval between measurement points
points = 10 # smoothing decay time in points
dt = 10    # time interval between measurement points
points = 10 # smoothing decay time in points

sensors = [] # list of sensors for the drivecage

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.info("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.will_set(topic, payload="99999", qos=1, retain=True)
    client.connect(broker, port)
    return client

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def publish(client, message):
    msg = f"{message}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.info("Message sent successfully to %s: %s", topic, msg)
    else:
        logging.error("Failed to send message to topic %s", topic)
    
stop = False  

sensors = secrets['SENSORS0'].split(",") if sys.argv[1] == "0" else secrets['SENSORS1'].split(",") 
topic = topic + ("/cage-0" if sys.argv[1] == "0" else "/cage-1")
print(sensors)
print(topic)
print(sys.argv[1])

if __name__ == "__main__":
    logging.info("Starting...")
    
    k = 1. / points
    K = 1 - k
    k = k / len(sensors)
    temp = int(open(sensors[0]).read())
    
    def sighandler(signum, frame):
        global stop
        stop = True
        
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    is_posix = os.name == 'posix'
    if is_posix:
        signal.signal(signal.SIGQUIT, sighandler)
 
    client = connect_mqtt()
    client.loop_start()
               
    while not stop:    
        time.sleep(dt)
        t = 0
        for s in sensors:
            t += int(open(s).read())
        temp = round(temp * K + t * k)
        print(temp)
        publish(client,temp)
        
    logging.info("Stopping...")
    publish(client,"99999")