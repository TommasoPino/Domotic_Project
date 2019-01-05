import time
import paho.mqtt.client as paho

broker="192.168.1.11"
#define callback
RecievedMessage = ""
CurrentStatus = "off"
RecievedNEWMessage = False
def on_message(client, userdata, message):
    global RecievedMessage 
    global RecievedNEWMessage
    time.sleep(1)
    RecievedMessage = str(message.payload.decode("utf-8")).lower()
    RecievedNEWMessage = True
    # print("received message =",str(message.payload.decode("utf-8")))

client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
client.on_message=on_message
#####
# print("connecting to broker ",broker)
client.connect(broker)#connect

# print("subscribing ")
client.subscribe("house/bulb1")#subscribe
# time.sleep(2)
# print("publishing ")
client.loop_start() #start loop to process received messages

# client.loop_forever() #start loop to process received messages
# client.publish("house/bulb1","on")#publish
# time.sleep(4)

while True:
    try:
        if RecievedNEWMessage:
            RecievedNEWMessage = False
            if RecievedMessage == "ON".lower():
                print('on')
                CurrentStatus = 'on'
                client.publish("house/bulb1/status",CurrentStatus)
            elif RecievedMessage == "OFF".lower():
                print('off')
                CurrentStatus = 'off'
                client.publish("house/bulb1/status",CurrentStatus)
            elif RecievedMessage == 'STATUS'.lower():
                print('status')
                client.publish("house/bulb1/status",CurrentStatus)
    except KeyboardInterrupt:
        break

client.disconnect() #disconnect
client.loop_stop() #stop loop
