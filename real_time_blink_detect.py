import numpy as np
import pandas as pd
from scipy.signal import medfilt
from scipy import signal
import time
import threading
import gevent
import csv
import sys
from Credentials import client_id, client_secret
from EmotivControl import Emotiv_API
from RT_Plot import *
from BluetoothControl import *
list_channels=["EEG.AF3", "EEG.F7", "EEG.F8", "EEG.AF4"]

class RealTimeBlinkEeg(object):
    
    def __init__(self, emotiv, F7_raw, F8_raw, F7, F8, _time, _time1, left_flag, right_flag, command, path):
        self.emotiv = emotiv
        data_file_eeg = pd.read_csv(path)
        self.eeg_data = data_file_eeg[list_channels]
        self.len_sig = self.eeg_data.shape[0]
        #padsize for padding signal 
        self.pad_size = 127
        #Sample frequency
        self.Fs = 128
        #Sample time
        self.Ts = 1/self.Fs
        #Threshold for peak detect
        self.threshold_left = 400
        self.threshold_right = 1000
        # counter service for get data from file eeg data
        self.count = 0
        # Create a Highpass filter
        # Sampling frequency: Fs = 128
        # Cut off frequency:  Fc = 0.5
        # Filter oder: 1
        self.hp_filter = signal.butter(1, 0.5, 'hp', fs=self.Fs, output='sos')
        self.window_size = 128
        self.F7_raw = F7_raw
        self.F8_raw = F8_raw
        self.F7_filtered = F7
        self.F8_filtered = F8
        self._F7 = []
        self._F8 = [] 
        self.left_flag = left_flag
        self.right_flag = right_flag
        self._time = _time
        self._time1 = _time1
        self.right_blink_count = 0
        self.left_blink_count = 0
        self.command = command
    def get_single_data(self):
        # single_data = self.eeg_data.loc[self.count, list_channels]
        # self.count += 1
        # return single_data['EEG.F7'], single_data['EEG.F8']

        single_data = self.emotiv.recv()
        # F7 = 3, F8 = 14
        return single_data.get('eeg')[3], single_data.get('eeg')[14]

    def filter_data(self, _signal):
        signal_pp_filtered = signal.sosfilt(self.hp_filter, _signal)
        # median filter
        # Filter oder: 13
        signal_filtered = medfilt(signal_pp_filtered,13)
        return signal_filtered

    def classify_blink(self, left_channel, right_channel):
        if left_channel > self.threshold_left:
            self.left_flag.append(1)
            self.left_blink_count += 1
        else: 
            self.left_blink_count = 0
            self.left_flag.append(0)
        if right_channel > self.threshold_right:
            self.right_blink_count += 1
            self.right_flag.append(1)
        else: 
            self.right_blink_count = 0
            self.right_flag.append(0)
        if len(self.left_flag) >= 1000:
            self.left_flag.pop(0)
        if len(self.right_flag) >= 1000:
            self.right_flag.pop(0)
        
        if self.left_blink_count == 10 and self.right_blink_count == 0:
            #print("left")
            command.append('F')
            pass
        elif self.right_blink_count == 10 and self.left_blink_count == 0:
            #print("right")
            command.append('B')
            pass
        elif self.right_blink_count > 0 and self.right_blink_count > 0:
            #print("left & right")
            command.append('S')
            pass

    def preprocess_signal(self, signal):
        signal_filtered = self.filter_data(signal)
        #peaks = self.peaks_detect(signal_filtered, self.threshold) 
        return signal_filtered
          
    def process_data(self, EEG_F7, EEG_F8):
        #start = time.time()

        a = self.preprocess_signal(EEG_F7)[127]
        b = self.preprocess_signal(EEG_F8)[127]

        self.classify_blink(a, b)
        self.F7_filtered.append(a)
        self.F8_filtered.append(b)
        self._time1.append(self._time1[-1] + 1)          
        if len(self.F7_filtered) >= 1000:
            self.F7_filtered.pop(0)
            self.F8_filtered.pop(0)
            self._time1.pop(0)
      
        #end = time.time()
        #runtime = end - start
        #print("Process data runtime:", runtime)

    def init_pad(self,pad_size):     
        for _ in range(pad_size):
            F7, F8 = self.get_single_data()
            self._F7.append(F7)
            self._F8.append(F8)
            self.F7_raw.append(F7)
            self.F8_raw.append(F8)
            self.left_flag.append(0)
            self.right_flag.append(0)
            self.F7_filtered.append(0)
            self.F8_filtered.append(0)
            if len(self._time) == 0:
                self._time.append(0)
            else:
                self._time.append(self._time[-1] + 1)
            if len(self._time1) == 0:
                self._time1.append(0)
            else:
                self._time1.append(self._time1[-1] + 1)                   
                
    def main_process(self):
        self.init_pad(self.pad_size)
        while True:
            #start = time.time()
            #add new data point
            #time.sleep(0.001)
            F7, F8 = self.get_single_data()
            self.F7_raw.append(F7)
            self.F8_raw.append(F8)
            self._time.append(_time[-1] +1)
            if len(self.F7_raw) >= 1000:
                self.F7_raw.pop(0)
                self.F8_raw.pop(0)
                self._time.pop(0)
            self._F7.append(F7)
            self._F8.append(F8)
            #time_step1 = time.time()
            real_time_eeg.process_data(self._F7.copy(), self._F8.copy())
            self._F7.pop(0)
            self._F8.pop(0)
            #time.sleep(0.001)
            #end = time.time()
            #time_run = end - start
            #print("Time run Collect data:",time_step1-start)
            #if time_run > 0.007:
            #print("Main process runtime:",time_run)
            #print()
 
def send_command(command):
    global old_len
    while True:
        new_len = len(command)
        if new_len != old_len:
            SendToBluetooth(command[-1])
            print("new_len: {}".format(new_len))
            print("old_len: {}".format(old_len))
            old_len = len(command)

def init_ble():
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

if __name__ == "__main__":
    try:
        emotiv = Emotiv_API(client_id, client_secret)
        emotiv.subscribe(["eeg"])
        emotiv.recv()
        # bluetooth setup:
        init_ble()
        threads = []
        F7 = []
        F8 = []
        F7_raw = []
        F8_raw = []
        _time = []
        _time1 = []
        left_flag = []
        right_flag = []
        old_len = 0
        command = []
        path = "D:\\Phu_Le\\Locker\\Emotiv_App\\CommunityCortexApp\\eeg_data\\Data_eeg.csv"
        real_time_eeg = RealTimeBlinkEeg(emotiv, F7_raw, F8_raw, F7, F8, _time, _time1, left_flag, right_flag, command, path)
        t = threading.Thread(target = real_time_eeg.main_process)
        t.start()
        threads.append(t)
        t1 = threading.Thread(target = send_command, args = (command,))
        t1.start()
        threads.append(t1) 
        main(F7, F8, _time1, left_flag, right_flag)
    except KeyboardInterrupt:
        print("Keyboard interrupt exiting program...")

    finally:
        print("Finally exiting program ...") 