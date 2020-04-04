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


list_channels=["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1", 
                "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"]

class RealTimeBlinkEeg(object):
    count = 0
    threshold = 100
    len_sig =0 
    eeg_data = []
    #Sample frequency
    Fs = 0
    #Sample time
    Ts = 0
    timeout = 0
    # Unit second
    session_time = 0
    num_of_sample_session = 0
    # Create a Higpass filter
    # Sampling frequency: Fs = 128
    # Cut off frequency:  Fc = 0.5
    # Filter oder: 1
    #eeg_fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=4, constrained_layout=True)
    hp_filter =0

    def __init__(self, path = "J:\\Backup Hdd 12 mar 2020\\test eeg python\\eeg_data\\Data_eeg.csv"):
        data_file_eeg = pd.read_csv(path)
        self.eeg_data = data_file_eeg[list_channels]
        self.len_sig = self.eeg_data.shape[0]
        #Sample frequency
        self.Fs = 128
        #Sample time
        self.Ts = 1/self.Fs
        self.timeout = 30
        self.session_time = 1
        self.num_of_sample_session = int(self.session_time * self.Fs)
        # Create a Higpass filter
        # Sampling frequency: Fs = 128
        # Cut off frequency:  Fc = 0.5
        # Filter oder: 1
        self.hp_filter = signal.butter(1, 0.5, 'hp', fs=128, output='sos')
        #Style for plot eeg graph
        #plt.style.use('seabom')
        self.results_header = []
        for channel in list_channels:
            self.results_header.append('peak_' + channel)
            self.results_header.append(channel)
        eeg_raw_header = list_channels.copy()
        eeg_raw_header.insert(0,"Index") 
        eeg_filted_header = self.results_header.copy()
        eeg_filted_header.insert(0,"Index")       
        with open('filted_eeg.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=eeg_filted_header)
            csv_writer.writeheader()        
        with open('eeg_raw.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=eeg_raw_header)
            csv_writer.writeheader()
        
        
    def get_single_data(self):
        single_data = self.eeg_data.loc[self.count, list_channels]
        self.count += 1
        return single_data

    def filt_data(self,eeg_data):
        Eeg_Hp_Filtered = signal.sosfilt(self.hp_filter, eeg_data)
        # median filter
        # Filter oder: 7
        Eeg_Filtered = medfilt(Eeg_Hp_Filtered,7)
        return Eeg_Filtered

    def peaks_detect(self, channels, threshold):
        peaks, _ = find_peaks(channels, height=threshold)
        return peaks

    def determine_blink_type(self, frame_eeg_filted, peaks_in_frame_eeg):

        pass

    def write_csv(self, frame_eeg, path):
        frame_eeg.to_csv(path,mode='a',header = False)

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
        frame_eeg_filted = self.filt_data(frame_eeg)
        peaks_in_frame_eeg = self.peaks_detect(frame_eeg_filted, self.threshold) 
        return frame_eeg_filted, peaks_in_frame_eeg
          
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
            #print(results_df.shape)          
            self.write_csv(results_df.drop(results_df.index[0:512]),'filted_eeg.csv')
        # for i in list_channels:
        #     frame_eeg_filted = self.filt_data(frame_eeg[i].values)
        #     peaks_in_frame_eeg = self.peaks_detect(frame_eeg_filted, self.threshold)     
        #     self.determine_blink_type(frame_eeg_filted, peaks_in_frame_eeg)
            
        end = time.time()
        runtime = end - start
        print("Process data runtime:", runtime)

    def main_process(self):
        threads = []
        print("start program")
        init = True
        init_time = 0
        frame_eeg = self.collect_data()
        try:
            while True:
                start = time.time()
                if init == True:
                    frame_eeg = frame_eeg.append(self.collect_data(), ignore_index = True)
                    init_time +=1
                    if init_time == 4:
                        init = False
                else:
                    frame_eeg = frame_eeg.drop(frame_eeg.index[0:128])
                    print("frame eeg shape after drop:{}".format(frame_eeg.shape))
                    single_frame = self.collect_data()
                    print("single frame shape:{}".format(single_frame.shape))
                    frame_eeg = frame_eeg.append(single_frame, ignore_index = True)
                    print("frame eeg shape:{}".format(frame_eeg.shape))
                    time_step1 = time.time()

                    write_csv_thread = threading.Thread(target=real_time_eeg.write_csv, args=(single_frame,'eeg_raw.csv'))
                    threads.append(write_csv_thread)
                    write_csv_thread.start()

                    process_thread = threading.Thread(target=real_time_eeg.process_data, args=(frame_eeg,))
                    threads.append(process_thread)
                    process_thread.start()

                    time.sleep(0.5)
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