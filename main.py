print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

#TODO: Add your token and your comport
#Please check the comport in the device manager
#V8Wlen76eZVHqNu9wfgy
THINGS_BOARD_ACCESS_TOKEN = "N7ijoZMl37XM2TrClKgZ"
bbc_port = "COM6"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    print(f'serial {data}')
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    #TODO: Add your source code to publish data to the server
    if splitData[1] == 'LED':
        json_data = {'LEDvalue': splitData[2]=='true'}
        client.publish('v1/devices/me/attributes', json.dumps(json_data))
    
    if splitData[1] == 'FAN':
        json_data = {'FANvalue': splitData[2]=='true'}
        client.publish('v1/devices/me/attributes', json.dumps(json_data))
    
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = -1
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['LEDvalue'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            cmd = 1 if temp_data['LEDvalue'] else 0
        if jsonobj['method'] == "setFAN":
            temp_data['FANvalue'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            cmd = 3 if temp_data['FANvalue'] else 2
    except:
        pass
    if cmd == -1:
        return

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

while True:
    if len(bbc_port) >  0:
        readSerial()

    time.sleep(1)