import time
import keyboard  # using module keyboard
def record(t):
    makers = []
    time_makers = []
    while t[-1] < 127:  # making a loop
        if keyboard.is_pressed('\n'):  # if key 'q' is pressed 
            print('You Pressed ENTER Key!')
            makers.append('L')
            time_makers.append(t[-1])            
            time.sleep(1)
        if keyboard.is_pressed(' '):  # if key 'q' is pressed 
            print('You Pressed SPACE Key!')
            makers.append('R')
            time_makers.append(t[-1])            
            time.sleep(1)
    with open('Makers.txt', 'w') as makers_file: 
        for i in makers:
            makers_file.write(str(i))
            makers_file.write('\n')
        for i in time_makers:
            makers_file.write(str(i))
            makers_file.write('\n')     
def auto_record(t):
    makers  = []
    time_makers = []
    for _ in range(10):
        time.sleep(3)
        makers.append('L')
        time_makers.append(t[-1])   
    time.sleep(11)
    for _ in range(10):
        time.sleep(3)  
        makers.append('R')
        time_makers.append(t[-1])   

    with open('Makers.txt', 'w') as makers_file: 
        for i in makers:
            makers_file.write(str(i))
            makers_file.write('\n')
        for i in time_makers:
            makers_file.write(str(i))
            makers_file.write('\n')                            
