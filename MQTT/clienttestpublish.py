import time
import paho.mqtt.client as paho
import sys

broker="192.168.1.11"
#define callback
def on_message(client, userdata, message):
    time.sleep(0.5)
    print(str(message.payload.decode("utf-8")))

clientTopic = sys.argv[1]
message = sys.argv[2]

client= paho.Client("server") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
client.on_message=on_message
# #####
# print("connecting to broker ",broker)
client.connect(broker)#connect
# client.loop_start() #start loop to process received messages
# print("subscribing ")
# client.subscribe("house/bulb1")#subscribe
# time.sleep(2)
# print("publishing ")
# client.publish("house/bulb1","on")#publish
# client.publish("84:f3:eb:0c:34:1d","PIN,0,"+)

client.publish(clientTopic,message)


# time.sleep(4)

client.subscribe(clientTopic+"/status")
client.loop_start()
time.sleep(5)
client.disconnect() #disconnect
client.loop_stop() #stop loop
