import bluetooth
import time
# global variables for module
startMarker = '<'
endMarker = '>'
InputBuffer =""
ReadInProcess = False
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
def SearchNearBy():
    Ble_Dict = {}
    #Look for all Bluetooth devices
    #the computer knows about.
    print ("Searching for devices...")
    print ("")
    #Create an array with all the MAC
    #addresses of the detected devices
    nearby_devices = bluetooth.discover_devices()
    #Run through all the devices found and list their name
    for i in nearby_devices:
	    Ble_Dict[bluetooth.lookup_name(i)] = i
    return Ble_Dict
# ========================
def CreatConection(bd_addr):

    global sock
    port = 1
    sock.connect((bd_addr, port))
    waitForArduino()
# ========================
def CloseConection():
    sock.close()
# ========================
def SendToBluetooth(SendStr):
    global startMarker, endMarker,sock

    sock.send(startMarker)
    sock.send(SendStr)
    sock.send(endMarker)
#=========================
def recvFromArduino(timeOut):
    global ReadInProcess, InputBuffer    
    data = sock.recv(1).decode('utf-8')
    if (data == endMarker):
        ReadInProcess = False
        #print(InputBuffer)
        return InputBuffer
    if (ReadInProcess == True):
        InputBuffer += data
    if (data == startMarker):
        ReadInProcess = True 
        InputBuffer = ""      
    #print("received [%s]" % data)   
    return '0'
# ========================
def waitForArduino():
    # wait until the Arduino sends'Arduino Ready'-allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are
    # discarded
    print ("Waiting for Arduino to reset...")
    msg = ""
    while msg.find("Arduino is ready") == -1:
        SendToBluetooth("PC is ready")
        msg = recvFromArduino(10)
        if (msg[0] != '0'):
            print(msg)
# ==========================    

    
    