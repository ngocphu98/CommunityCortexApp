
#------------------------------------------------
# Importing the packages and the libraries
from BluetoothControl import *
from Credentials import *
import json
from websocket  import create_connection
import ssl
import time
import requests
ws = create_connection("wss://localhost:6868", sslopt={"cert_reqs": ssl.CERT_NONE})
#------------------------------------------------------------
#Get cortex info
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getCortexInfo"
}))
result = json.loads(ws.recv())
print("BuildDate: ",result["result"]["buildDate"])
print("BuildNumber: ",result["result"]["buildNumber"])
print("Version: ",result["result"]["version"])
#------------------------------------------------------------
#get User login
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getUserLogin"
}))
result = json.loads(ws.recv())
print("CurrentOSUId: ",result["result"][0]["currentOSUId"])
print("CurrentOSUsername: ",result["result"][0]["currentOSUsername"])
print("LoggedInOSUId: ",result["result"][0]["loggedInOSUId"])
print("LoggedInOSUsername: ",result["result"][0]["loggedInOSUsername"])
#------------------------------------------------------------
#Query Headsets ID
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "queryHeadsets"
}))
result = json.loads(ws.recv())
if (len(result["result"]) > 0 ):
    IdHeadset = result.get("result")[0].get("id")    
    print("Conected to Headset ID: %s" %(IdHeadset))
else:
    print("No headset conected.\nPlease conect the headset!")
    exit()

#------------------------------------------------------------
# #Get request access
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "requestAccess",
    "params": {
        "clientId": client_id,
        "clientSecret": client_secret
    }
}))
print(ws.recv())
#------------------------------------------------------------
#Authorize
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "authorize",
    "params": {
        "clientId": client_id,
        "clientSecret": client_secret
    }
}))
result = json.loads(ws.recv())
CortexToken = result.get("result").get("cortexToken")
print(result)   
#------------------------------------------------------------
#Creat new session
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "createSession",
    "params": {
        "cortexToken": CortexToken,
        "headset": IdHeadset,
        "status": "open"
    }
}))
result = json.loads(ws.recv())
IdSession = result.get("result").get("id")
#------------------------------------------------------------
#Load profile
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "setupProfile",
    "params": {
        "cortexToken": CortexToken,
        "headset": IdHeadset,
        "profile": ProfileName,
        "status": "load"
    }
}))
#------------------------------------------------------------
#Stream data
ws.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "subscribe",
    "params": {
        "cortexToken": CortexToken,
        "session": IdSession,
        "streams": ["com"]
    }
}))

List = SearchNearBy()
num = 0
NameBle = []
#print nearby bluetool device
for k, v in List.items():
    NameBle += [k]
    num += 1
    print ("{}:".format(num)," \t:\t ".join((k,v)))
print ("Select your device by entering its coresponding number...")
selection = int(input("> "))-1
print ("You have selected", NameBle[selection])
CreatConection(List[NameBle[selection]])
print("Conected.")
while True:
    result = json.loads(ws.recv())
    MentalCommand = result.get("com")
    if(MentalCommand != None):
        print(MentalCommand[0],MentalCommand[1])
        SendToBluetooth(MentalCommand[0])
        SendToBluetooth(str(MentalCommand[1]))