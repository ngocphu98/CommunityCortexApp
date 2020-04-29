import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.signal import medfilt
from scipy import signal
import time
import threading
import concurrent.futures
import gevent
import csv
from queue import Queue
from EmotivControl import Emotiv_API

list_channels=["EEG.F7", "EEG.F8"]

class RealTimeBlinkEeg(object):
    
    def __init__(self, path = "D:\\NghienCuuKhoaHoc2019\\Programming\\CommunityCortexApp\\eeg_data\\Data_eeg.csv"):
        data_file_eeg = pd.read_csv(path)
        self.eeg_data = data_file_eeg[list_channels]
        self.len_sig = self.eeg_data.shape[0]
        #padsize for padding signal 
        self.pad_size = 8
        #Sample frequency
        self.Fs = 128
        #Sample time
        self.Ts = 1/self.Fs
        #time out for collecting data unit (s)
        self.timeout = 30
        # session (s) length of signal to process
        self.session_time = 0.25
        self.num_of_sample_session = int(self.session_time * self.Fs)
        #Threshold for peak detect
        self.threshold = 230
        # counter service for get data from file eeg data
        self.count = 0
        # Create a Highpass filter
        # Sampling frequency: Fs = 128
        # Cut off frequency:  Fc = 0.5
        # Filter oder: 1
        self.hp_filter = signal.butter(1, 0.5, 'hp', fs=self.Fs, output='sos')
        self.window_size = 128
        self.EEG_F7 = Queue(window_size)
        self.EEG_F8 = Queue(window_size)

        #header for file filted_eeg.csv'
        self.results_header = []
        for channel in list_channels:
            self.results_header.append('peak_' + channel)
            self.results_header.append(channel)
        eeg_raw_header = list_channels.copy()
        eeg_raw_header.insert(0,"Index") 
        eeg_filtered_header = self.results_header.copy()
        eeg_filtered_header.insert(0,"Index")   

        # Write header for file    
        with open('filted_eeg.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=eeg_filtered_header)
            csv_writer.writeheader()        
        with open('eeg_raw.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=eeg_raw_header)
            csv_writer.writeheader()
        
        
    def get_single_data(self):
        single_data = self.eeg_data.loc[self.count, list_channels]
        self.count += 1
        return single_data['EEG.F7'], single_data['EEG.F8']

    def filter_data(self,eeg_data):
        Eeg_Hp_Filtered = signal.sosfilt(self.hp_filter, eeg_data)
        # median filter
        # Filter oder: 7
        Eeg_Filtered = medfilt(Eeg_Hp_Filtered,13)
        return Eeg_Filtered

    def peaks_detect(self, channels, threshold):
        peaks, _ = find_peaks(channels, height=threshold)
        return peaks

    def classify_blink(self, eeg_data):
        if len(eeg_data[eeg_data['peak_EEG.AF3'] == 1]) >0 and len(eeg_data[eeg_data['peak_EEG.AF4'] == 1]) ==0:
            print("blink left eye")
        elif len(eeg_data[eeg_data['peak_EEG.AF3'] == 1]) ==0 and len(eeg_data[eeg_data['peak_EEG.AF4'] == 1]) >0:
            print("blink right eye")
        elif len(eeg_data[eeg_data['peak_EEG.AF3'] == 1]) >0 and len(eeg_data[eeg_data['peak_EEG.AF4'] == 1]) >0:
            print("blink 2 eye")
        print("----------------------------")
        

    def write_csv(self, frame_eeg, path):
    #append mode in writing to excel file
        frame_eeg.to_csv(path, mode='a', header = False)

    def collect_data(self):
        counter = 0
        session_data = pd.DataFrame(columns = list_channels)
        #print(session_data)
        timestart = time.time() 
        while counter <= (self.num_of_sample_session - 1):
            if (time.time() - timestart >= self.timeout):
                return "Collect data time out"
            else:
                new_single_data = self.get_single_data()
                session_data = session_data.append(new_single_data, ignore_index = True)
                #print(session_data)
                #print(counter)
                counter +=1
        return session_data

    def preprocess_signal(self, frame_eeg):
        frame_eeg_filtered = self.filter_data(frame_eeg)
        peaks_in_frame_eeg = self.peaks_detect(frame_eeg_filtered, self.threshold) 
        return frame_eeg_filtered, peaks_in_frame_eeg
          
    def process_data(self,frame_eeg):
        start = time.time()
        #print("frame eeg shape{}".format(frame_eeg.shape))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(self.preprocess_signal, frame_eeg[channel].values) for channel in list_channels]
            results_df = pd.DataFrame(columns = self.results_header)
            i = 0
            for f in results:
                #print(type(f.result()))
                result = f.result()
                peak = np.zeros(len(result[0]))
                peak[result[1]] = 1
                results_df[self.results_header[i+1]] = result[0]
                results_df[self.results_header[i]] = peak
                i += 2   
            results_df =  results_df.drop(results_df.index[0:self.pad_size*self.num_of_sample_session])
            #print(results_df.shape)   
            self.classify_blink(results_df)
            #self.write_csv(results_df, 'filted_eeg.csv')

        end = time.time()
        runtime = end - start
        print("Process data runtime:", runtime)

    def init_pad(self,pad_size):
        frame_eeg = self.collect_data()        
        for _ in range(pad_size):
            frame_eeg = frame_eeg.append(self.collect_data(), ignore_index = True) #enqueue
            EEG_F7, EEG_F8 = get_single_data()
            self.EEG_F7.enqueue(EEG_F7)
            self.EEG_F8.enqueue(EEG_F8)
        return frame_eeg  

    def main_process(self):
        threads = []
        print("start program")
        frame_eeg = self.init_pad(self.pad_size)
        try:
            while True:
                start = time.time()
                frame_eeg = frame_eeg.drop(frame_eeg.index[0:self.num_of_sample_session])
                #print("frame eeg shape after drop:{}".format(frame_eeg.shape))
                single_frame = self.collect_data()
                #print("single frame shape:{}".format(single_frame.shape))
                frame_eeg = frame_eeg.append(single_frame, ignore_index = True)
                #print("frame eeg shape:{}".format(frame_eeg.shape))
                time_step1 = time.time()

                write_csv_thread = threading.Thread(target=real_time_eeg.write_csv, args=(single_frame,'eeg_raw.csv'))
                threads.append(write_csv_thread)
                write_csv_thread.start()

                process_thread = threading.Thread(target=real_time_eeg.process_data, args=(frame_eeg,))
                threads.append(process_thread)
                process_thread.start()

                #time.sleep(0.1)
                end = time.time()
                time_run = end - start

                print("Time run Collect data:",time_step1-start)
                print("Main process runtime:",time_run)

        except KeyboardInterrupt:
            print("Keyboard interrupt exiting program ...")
        finally:
            print("Finally exiting program ...")
              
if __name__ == "__main__":
	real_time_eeg = RealTimeBlinkEeg()
	real_time_eeg.main_process()