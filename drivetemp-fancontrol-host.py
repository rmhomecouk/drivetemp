#!/usr/bin/python3

import time, os, random, logging, signal, sys
from paho.mqtt import client as mqtt_client
from dotenv import dotenv_values

secrets = dotenv_values(".env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(secrets["LOG_LEVEL"].upper()) # set log level from .env file

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

stop = False  

dt = 10    # time interval between measurement points
points = 10 # smoothing decay time in points

outfile_cage0 = os.path.expanduser("/var/tmp/drivetemp-cage-0.txt")
outfile_cage1 = os.path.expanduser("/var/tmp/drivetemp-cage-1.txt")

logging.info("Topic: %s", topic)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)    
    client.on_message = on_message
    client.subscribe('drivetemp/cage-0')
    client.subscribe('drivetemp/cage-1')
    return client

def on_message(client, userdata, msg):
    logging.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    if msg.topic == 'drivetemp/cage-0':            
        if not os.path.exists(outfile_cage0):
            open(outfile_cage0, "w").close()
        myfile = open(outfile_cage0,'r+')
        myfile.seek(0)
        myfile.write(str(int(msg.payload.decode())) + "\n\n")
        myfile.truncate()
    if msg.topic == 'drivetemp/cage-1':            
        if not os.path.exists(outfile_cage1):
            open(outfile_cage1, "w").close()
        myfile = open(outfile_cage1,'r+')
        myfile.seek(0)
        myfile.write(str(int(msg.payload.decode())) + "\n\n")
        myfile.truncate()

def on_disconnect(client, userdata, rc):
    logging.warn("Disconnected with result code: %s", rc)
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
    logging.error("Reconnect failed after %s attempts. Exiting...", reconnect_count)

if __name__ == "__main__":
    logging.info("Starting...")

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
        
    logging.info("Stopping...")