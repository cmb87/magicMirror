import paho.mqtt.client as mqtt
from db.database import Database
from datetime import datetime
import logging
from configparser import ConfigParser

# Set logging formats
logging.basicConfig(
    level=logging.INFO,#{"info": logging.INFO, "critical": logging.CRITICAL}[flags.loggingLevel],
    format=("[%(filename)8s] [%(levelname)4s] :  %(funcName)s - %(message)s"),
)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("sensor1/humidity")
    client.subscribe("sensor1/temperature")
    client.subscribe("sensor2/humidity")
    client.subscribe("sensor2/temperature")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    aux = msg.topic.split("/")
    sensorName, sensorType = aux[0], aux[1]
    sensorValue = float(msg.payload)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    row = [{
        "time": time, "sensorname": sensorName,
        "sensortype": sensorType, "sensorvalue": sensorValue
    }]

    logging.info("Adding entry")

    Database.insert(TABLENAME, row)

    logging.info("New entry added")

# ===============================

TABLENAME = "climate"
parser = ConfigParser()
parser.read(Database.DBCONFIG)
config = dict(parser._sections['mqttbroker'])


if __name__ == '__main__':

    # Create table
    if not Database.checkIfTableExists(TABLENAME):

        # Columns
        columns = {
            "id": "SERIAL PRIMARY KEY", "sensorname": "TEXT",
            "sensortype": "TEXT", "sensorvalue": "FLOAT", "time":"TIMESTAMP"
        }

        Database.create_table(TABLENAME, columns)
        logging.info("Table created")

    # Connect and run
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config["host"], int(config["port"]), 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

    #mqttc.publish("paho/temperature", temperature)
