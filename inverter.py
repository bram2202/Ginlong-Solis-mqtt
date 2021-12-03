#!/usr/bin/python3

import time
import schedule
import requests
import random
import serial
import minimalmodbus
from datetime import datetime
from paho.mqtt import client as mqtt_client

# Setup minimalmodbus
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 3

# MQTT settings
mqtt_broker = "<BROKER_IP>"
mqtt_port = 1883
mqtt_user = "<UserName>"
mqtt_password = "<Password>"
mqtt_client_id = f'python-mqtt-{random.randint(0, 1000)}'

pv_api_key = "<PvOutputApiKey>"
pv_system_id = "<PvOutputSystemId>"

# Read values from invertor with RS485
def getValues():
    global Realtime_ACW, Realtime_DCV, Realtime_DCI, Realtime_ACV, Realtime_ACI, Realtime_ACF, Inverter_C, Alltime_KWH, Today_KWH, LastMeasurement
    # AC Watts
    Realtime_ACW = instrument.read_long(3004, functioncode=4, signed=False)
    # DC volts 
    Realtime_DCV = instrument.read_register(3021, functioncode=4, signed=False) / 10
    # DC current 
    Realtime_DCI = instrument.read_register(3022, functioncode=4, signed=False) /10
    # AC volts 
    Realtime_ACV = instrument.read_register(3035, functioncode=4, signed=False) / 10
    # AC current 
    Realtime_ACI = instrument.read_register(3038, functioncode=4, signed=False) / 10
    # AC frequency
    Realtime_ACF = instrument.read_register(3042, functioncode=4, signed=False) / 100
    # Inverter temperature 
    Inverter_C = instrument.read_register(3041, functioncode=4, signed=True) / 10
    # All time energy (kWh total) 
    Alltime_KWH = instrument.read_long(3008, functioncode=4, signed=False)
    # Todays energy (kWh total) 
    Today_KWH = instrument.read_register(3014, functioncode=4, signed=False) / 10

    LastMeasurement = datetime.now()

# Print values for debugging
def printValues():    
    print("AC Watts: " + str(Realtime_ACW) + " W")
    print("DC Volt: " + str(Realtime_DCV) + " V")
    print("DC Current: " + str(Realtime_DCI) + " A")
    print("AC volt: " + str(Realtime_ACV) + " V")
    print("AC Current: " + str(Realtime_ACI) + " A")
    print("AC Frequency: " + str(Realtime_ACF) + " Hz")
    print("Inverter temperature: " + str(Inverter_C) + " C")
    print("Generated all time: " + str(Alltime_KWH) + " kWh")
    print("Generated today: " + str(Today_KWH) + " kWh")

# Create MQTT connection
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(mqtt_client_id)
    client.username_pw_set(mqtt_user, mqtt_password)
    client.on_connect = on_connect
    client.connect(mqtt_broker, mqtt_port)
    return client

# Send values to MQTT
def sendMqtt(client):
    client.loop_start()
    client.publish("pv/ac", '{"W":"' + str(Realtime_ACW) + '", "V":"' + str(Realtime_ACV) + '", "C":"' + str(Realtime_ACI) + '", "F":"' + str(Realtime_ACF) + '"}', qos=0, retain=False)
    client.publish("pv/dc", '{"V":"' + str(Realtime_DCV) + '", "C":"' + str(Realtime_DCI) + '"}', qos=0, retain=False)
    client.publish("pv/gen", '{"D":"' + str(Today_KWH) + '", "T":"' + str(Alltime_KWH) + '"}', qos=0, retain=False)
    client.publish("pv/temp", '{"T":"' + str(Inverter_C) + '"}', qos=0, retain=False)
    client.disconnect()
    client.loop_stop()

# Call all functions for reading and sending
def readAndSendData():
    try:
        getValues()
        #printValues()
        client = connect_mqtt()
        sendMqtt(client)
    except Exception as err:
        print("--ERROR: ")
        print(err)

# Send measurements to PV output
def sendPvOutput():
    now = datetime.now()

    # Check if LastMeasurement is set
    if not 'LastMeasurement' in globals():
        return

    # If measurements are old, don't send (inverter off)
    duration = datetime.now() - LastMeasurement 
    minutes = divmod(duration.total_seconds(), 60)[0]  
    if minutes > 4:
        return
   
    # Create header for auth
    header = {
        "X-Pvoutput-Apikey" : pv_api_key,
        "X-Pvoutput-SystemId" : pv_system_id
    }

    # Create body for PV output
    # https://pvoutput.org/help/api_specification.html#add-output-service
    body = {
        "d" : now.strftime("%Y%m%d"),
        "t" : now.strftime("%H:%M"),
        "v1" : str(Today_KWH * 1000),
        "v2" : str(Realtime_ACW),
        "v5" : str(Inverter_C),
        "v6" : str(Realtime_DCV)
    }

    # Post status
    session = requests.Session()
    session.headers.update(header)
    response = session.post("https://pvoutput.org/service/r2/addstatus.jsp", data=body)

# Main function, called on start
if __name__ == '__main__':
    print("-- Start script --")

    # Create scheduler
    schedule.every(5).seconds.do(readAndSendData)
    schedule.every(5).minutes.do(sendPvOutput) # needs to be 5 minimum

    while 1:
        schedule.run_pending()
        time.sleep(1)