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
import math
from scipy.signal import find_peaks, savgol_filter
list_channels=["EEG.AF3", "EEG.F7", "EEG.F8", "EEG.AF4"]

class RealTimeBlinkEeg(object):
    
    def __init__(self, emotiv, F7_raw, F8_raw, F7, F8, _time, _time1, left_flag, right_flag, command):
        self.emotiv = emotiv
        #padsize for padding signal 
        self.pad_size = 127
        #Sample frequency
        self.Fs = 128
        #Sample time
        self.Ts = 1/self.Fs
        #Threshold for peak detect
        self.threshold_left = 800
        self.threshold_right = 800
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
        self.kq = []
        self.Time = []
        self.left_lock_count = 0
        self.right_lock_count = 0
        self.left = False
        self.right = False
        self.wait_right = 0
        self.wait_left = 0
        self.left_check = False
        self.right_check = False
        self.c = 0
        # self.AccX = []
        # self.AccY = []
        # self.AccZ = []

    def get_single_data(self):
        single_data = self.emotiv.recv()
        # F7 = 3, F8 = 14
        #AF3 = 2, AF4 = 13
        return single_data

    def filter_data(self, _signal):
        signal_pp_filtered = signal.sosfilt(self.hp_filter, _signal)
        # median filter
        # Filter oder: 13
        signal_filtered = medfilt(signal_pp_filtered, 13)
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
        
        if left_flag[-1] == 1 and left_flag[-2] == 0:
            self.left = True
        else: 
            self.left = False

        if right_flag[-1] == 1 and right_flag[-2] == 0:
            self.right = True
        else: 
            self.right = False

        if self.right == True and self.left == True:
            print('Error')
            self.right = False
            self.left = False
        else:
            if self.left == True and self.left_lock_count == 0 and self.right_lock_count == 0:
                print('L', self._time1[-1])
                self.kq.append('L')
                command.append('4')
                self.Time.append(self._time1[-1])  
                self.left_lock_count = 50                

            if self.right == True and self.left_lock_count == 0 and self.right_lock_count == 0:
                print('R', self._time1[-1])
                self.kq.append('R')
                self.command.append('3')
                self.Time.append(self._time1[-1])
                self.right_lock_count = 50

        if self.right_lock_count > 0: 
            self.right_lock_count -= 1
        if self.left_lock_count > 0: 
            self.left_lock_count -= 1
    def classify_blink2(self, F7, F8):
        F7 = np.array(F7)
        F8 = np.array(F8)

        F7_pos_peak, pro = find_peaks(F7, height = self.threshold_left)
        F7_neg_peak, _ = find_peaks(-F7, height = 200)
        F8_pos_peak, _ = find_peaks(F8, height = self.threshold_right)
        F8_neg_peak, _ = find_peaks(-F8, height = 200)
        # print(F7_pos_peak)
        if len(F7_pos_peak) == 1 and len(F7_neg_peak) >= 1:
            # if F7_neg_peak[0] - F7_pos_peak[0] >= 30:
            self.kq.append('L')
            command.append('4')
            print('F7 Left: ',F7_neg_peak[0] - F7_pos_peak[0])
        if len(F8_pos_peak) == 1 and len(F8_neg_peak) >= 1:
            # if F8_neg_peak[0] - F8_pos_peak[0] >= 30:
            self.kq.append('R')
            self.command.append('3')            
            print('F8 Right: ',F8_neg_peak[0] - F8_pos_peak[0])
        print('----------------')
        # print(F8_pos_peak)
             
    def preprocess_signal(self, signal):
        signal_filtered = self.filter_data(signal)
        # signal_filtered = medfilt(signal_filtered, 31)
        signal_filtered = savgol_filter(signal_filtered,51, 2)
        #peaks = self.peaks_detect(signal_filtered, self.threshold) 
        return signal_filtered
          
    def process_data(self, EEG_F7, EEG_F8):
        #start = time.time()
        self.c += 1
        b = self.preprocess_signal(EEG_F8)[self.pad_size]
        a = self.preprocess_signal(EEG_F7)[self.pad_size]
        self.F7_filtered.append(a)
        self.F8_filtered.append(b)
        # self.classify_blink(a, b)
        if self.c == self.pad_size - 20:
            self.classify_blink2(self.F7_filtered[-1-self.pad_size:-1],self.F8_filtered[-1-self.pad_size:-1])
            self.c = 0
        self._time1.append(self._time1[-1] + self.Ts)
        #Save data and exit after a specific time
        # if self._time1[-1] >= 100:
        #     with open('Result.txt', 'w') as result_file: 
        #         for i in self.kq:
        #             result_file.write(str(i))
        #             result_file.write('\n')
        #         for i in self.Time:
        #             result_file.write(str(i))
        #             result_file.write('\n') 
        #     exit(0)                     
        if len(self.F7_filtered) >= 1000:
            self.F7_filtered.pop(0)
            self.F8_filtered.pop(0)
            self._time1.pop(0)
      
        #end = time.time()
        #runtime = end - start
        #print("Process data runtime:", runtime)

    def init_pad(self,pad_size):    
        i = 0 
        while i < pad_size:
            single_data = self.emotiv.recv()
            if 'eeg' in single_data:
                F7 = single_data.get('eeg')[3]
                F8 = single_data.get('eeg')[14]                
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
                    self._time1.append(self._time1[-1] + self.Ts)
                i += 1                   
                
    def main_process(self):
        self.init_pad(self.pad_size)
        c = 0
        print('start at: {}'.format(self._time1[-1]))
        while True:
            #start = time.time()
            #add new data point
            #time.sleep(0.001)
            single_data = self.emotiv.recv()
            if 'eeg' in single_data:
                F7 = single_data.get('eeg')[3]
                F8 = single_data.get('eeg')[14]
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
                
            elif 'mot' in single_data:
                # self.AccX.append(single_data.get('mot')[5])
                # self.AccY.append(single_data.get('mot')[6])
                # self.AccZ.append(single_data.get('mot')[7])
                AccX = single_data.get('mot')[5]
                AccY = single_data.get('mot')[6]
                AccZ = single_data.get('mot')[7]               
                G = math.sqrt(AccX*AccX+AccY*AccY+AccZ*AccZ)
                if G > 12500:
                    # print(G)
                    self.right_lock_count = 300
                    self.left_lock_count = 300

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
            # print(command[-1])
            old_len = len(command)
        time.sleep(0.2)

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
        BLE = 0
        emotiv = Emotiv_API(client_id, client_secret)
        if BLE == 1:
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
        real_time_eeg = RealTimeBlinkEeg(emotiv, F7_raw, F8_raw, F7, F8, _time, _time1, left_flag, right_flag, command)
        t = threading.Thread(target = real_time_eeg.main_process)
        # input("nhan phim bat ki de dat dau")
        emotiv.subscribe(["eeg", "mot"])
        # emotiv.subscribe(["eeg"])
        print(emotiv.recv())
        t.start()
        if BLE == 1:
            threads.append(t)
            t1 = threading.Thread(target = send_command, args = (command,))
            t1.start()
            threads.append(t1)    
        main(F7, F8, _time1, left_flag, right_flag, command)
        # time.sleep(1)
        # from Record_Makers import *
        # auto_record(_time1)
    except KeyboardInterrupt:
        print("Keyboard interrupt exiting program...")
    finally:
        print("Finally exiting program ...")