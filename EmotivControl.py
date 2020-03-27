
#------------------------------------------------
# Importing the packages and the libraries
from BluetoothControl import *
from Credentials import *
import json
from websocket  import create_connection
import ssl
import time
import requests
from termcolor import colored
EmotivWebsocketUrl = "wss://localhost:6868"
try:
    EmotivWs = create_connection(EmotivWebsocketUrl, sslopt = {"cert_reqs": ssl.CERT_NONE})
except ConnectionRefusedError:
    print("Cannot connect to EmotivWebsocket.")
    print("Invalid URL. Please check the url!")
    exit(0)

#------------------------------------------------------------
#Get cortex info
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getCortexInfo"
}))
result = json.loads(EmotivWs.recv())
print("BuildDate: ",result["result"]["buildDate"])
print("BuildNumber: ",result["result"]["buildNumber"])
print("Version: ",result["result"]["version"])
#------------------------------------------------------------
#Get User login
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getUserLogin"
}))
result = json.loads(EmotivWs.recv())
print("CurrentOSUId: ",result["result"][0]["currentOSUId"])
print("CurrentOSUsername: ",result["result"][0]["currentOSUsername"])
print("LoggedInOSUId: ",result["result"][0]["loggedInOSUId"])
print("LoggedInOSUsername: ",result["result"][0]["loggedInOSUsername"])
#------------------------------------------------------------
#Query Headsets ID
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "queryHeadsets"
}))
result = json.loads(EmotivWs.recv())
if (len(result["result"]) > 0 ):
    IdHeadset = result.get("result")[0].get("id")    
    print(colored("Conected to Headset ID: %s" %(IdHeadset),"green"))
else:
    print(colored("No headset conected.\nPlease conect the headset!", "red"))
    exit(0)

#------------------------------------------------------------
#Get request access
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "requestAccess",
    "params": {
        "clientId": client_id,
        "clientSecret": client_secret
    }
}))
result = json.loads(EmotivWs.recv())
AccessGranted = result.get("result").get("accessGranted")
if(AccessGranted == False):
    print(colored("AccesGranted: %s "%str(AccessGranted),"red"))
    print(colored("Message: %s" %(result["result"]["message"]),"red"))
    print("Please approve request through EMOTIV App!")
    exit(0)
else:
    print(colored("AccesGranted: %s "%str(AccessGranted),"green"))
    print(colored("Message: %s" %(result["result"]["message"]),"green"))

    
#------------------------------------------------------------
#Authorize
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "authorize",
    "params": {
        "clientId": client_id,
        "clientSecret": client_secret
    }
}))
print("Waiting cortext Token...")   
result = json.loads(EmotivWs.recv())
CortexToken = result.get("result").get("cortexToken")
print(colored("successfuly","green"))   
#------------------------------------------------------------
#Creat new session
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "createSession",
    "params": {
        "cortexToken": CortexToken,
        "headset": IdHeadset,
        "status": "active"
    }
}))
result = json.loads(EmotivWs.recv())
print(result)
IdSession = result.get("result").get("id")
#------------------------------------------------------------
#Load profile
# EmotivWs.send(json.dumps({
#     "id": 1,
#     "jsonrpc": "2.0",
#     "method": "setupProfile",
#     "params": {
#         "cortexToken": CortexToken,
#         "headset": IdHeadset,
#         "profile": ProfileName,
#         "status": "load"
#     }
# }))
#------------------------------------------------------------
#Stream data 
#The parameter streams must contain one or more values, chosen from this list: 
# "eeg", "mot", "dev", "pow", "met", "com",  "fac", "sys". 
EmotivWs.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "subscribe",
    "params": {
        "cortexToken": CortexToken,
        "session": IdSession,
        "streams": ["eeg"]
    }
}))
#------------------------------------------------------------
print("1. Running program without BLE")
print("2. Runing initialize BLE and send data stream to Arduino")
print ("Select by entering coresponding number...")
SelectionRun = int(input(">"))
if (SelectionRun == 1):
    while True:
        result = json.loads(EmotivWs.recv())
        print(result)
        # ReturnData = result.get("com")
        # if(ReturnData != None):
        #     MentalCommand = ReturnData[0]
        #     ActionPower = ReturnData[1]
        #     Time = result["time"]
        #     print(MentalCommand,ActionPower,Time)
            

else:
    #BLE initialize
    List = SearchNearBy()
    num = 0
    NameBle = []
    #print nearby bluetooth device
    for k, v in List.items():
        NameBle += [k]
        num += 1
        print ("{}:".format(num)," \t:\t ".join((k,v)))
    print ("Select your device by entering its coresponding number...")
    SelectionDevice = int(input("> ")) - 1
    print ("You have selected", NameBle[SelectionDevice])
    CreatConection(List[NameBle[SelectionDevice]])
    print("Conected to ",NameBle[SelectionDevice])
    while True:
        result = json.loads(EmotivWs.recv())
        # ReturnData = result.get("com")
        # if(ReturnData != None):
        #     print(MentalCommand,ActionPower)
        #     SendToBluetooth(MentalCommand)
        #     SendToBluetooth(str(ActionPower))
        #     MentalCommand = ReturnData[0]
        #     ActionPower = ReturnData[1]
            
