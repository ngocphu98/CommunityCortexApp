from PyQt5 import QtWidgets, QtCore, QtGui, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
import time
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data_F7, data_F8, index, left_flag, right_flag, command, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.resize(1200,400)
        self.setWindowTitle("EEG-Blink")
        toolbar = QtWidgets.QToolBar("MY Tool BAR")
        self.addToolBar(toolbar)
        # toolbar.addAction("Threshold")
        # toolbar.addAction('Manual-Control')
        self.data_F7 = data_F7
        self.data_F8 = data_F8
        self.y_F7 = data_F7 
        self.y_F8 = data_F8
        self.index = index
        self.left_flag = left_flag
        self.right_flag = right_flag
        self.command = command
        self.robo = 2
        self.stop = -1
        graph_layout = QtWidgets.QVBoxLayout()
        layout1 = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        bt_layout = QtWidgets.QVBoxLayout()
        main_layout = QtWidgets.QVBoxLayout()
        self.F7_graphWidget = pg.PlotWidget()
        self.F7_graphWidget.setTitle("EEG F7", size="12pt")
        self.F7_graphWidget.setLabel('left', 'Amplitude (uV)')
        self.F7_graphWidget.setLabel('bottom', 'Time (s)')
        self.F7_graphWidget.setYRange(-2000,5000)
        # self.F7_thresholdWidget = QtWidgets.QSlider()
        # self.F7_thresholdWidget.setMinimum(-100)
        # self.F7_thresholdWidget.setMaximum(5000)
        # self.F7_thresholdWidget.valueChanged.connect(self.F7_value_change)
        self.F8_graphWidget = pg.PlotWidget()
        self.F8_graphWidget.setTitle("EEG F8", size="12pt")
        self.F8_graphWidget.setLabel('left', 'Amplitude (uV)')
        self.F8_graphWidget.setLabel('bottom', 'Time (s)')
        self.F8_graphWidget.setYRange(-2000, 5000)
        # self.F8_thresholdWidget = QtWidgets.QSlider()
        # self.F8_thresholdWidget.setMinimum(-100)
        # self.F8_thresholdWidget.setMaximum(5000)
        # self.F8_thresholdWidget.valueChanged.connect(self.F8_value_change)
        # lf = left_flag
        # rf = right_flag
        self.lf_graphWidget = pg.PlotWidget()
        self.lf_graphWidget.setYRange(0, 1)
        self.rf_graphWidget = pg.PlotWidget()
        
        self.F7_graphWidget.setBackground('#ffffff')
        self.F8_graphWidget.setBackground('#ffffff')
        self.lf_graphWidget.setBackground('#ffffff')
        self.rf_graphWidget.setBackground('#ffffff')
        
        # layout1.addWidget(self.F7_thresholdWidget)        
        graph_layout.addWidget(self.F7_graphWidget)
        # layout1.addWidget(self.F8_thresholdWidget)
        graph_layout.addWidget(self.F8_graphWidget)
        layout1.addLayout(graph_layout)
        self.label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(os.getcwd()+"//images//robo//robo (" + str(self.robo) +").png")
        pixmap = pixmap.scaled(430, 540, QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        layout1.addWidget(self.label)
        layout1.addLayout(bt_layout)
        self.stop_btn = QtWidgets.QPushButton(" STOP")
        self.stop_btn.setIcon(QtGui.QIcon(os.getcwd()+"//images//play.png"))
        self.stop_btn.setIconSize(QtCore.QSize(24,24))        
        self.stop_btn.setStyleSheet("QPushButton"
                                "{"
                                "background-color : #3ca59d;"
                                "font: bold 13px;"
                                "padding: 6px;" 
                                "border-radius: 10px;"
                                "}"
                                "QPushButton::pressed"
                                "{"
                                "background-color : red;"
                                "}"
                                ) 
        self.stop_btn.clicked.connect(self.stop_clicked)   

        self.up_btn = QtWidgets.QPushButton("   UP")
        self.up_btn.setIcon(QtGui.QIcon(os.getcwd()+"//images//up.png"))
        self.up_btn.setIconSize(QtCore.QSize(24,24))
        self.up_btn.setStyleSheet("QPushButton"
                                "{"
                                "background-color : #3ca59d;"
                                "font: bold 13px;"
                                "padding: 6px;" 
                                "border-radius: 10px;"
                                "}"
                                "QPushButton::pressed"
                                "{"
                                "background-color : red;"
                                "}"
                                )                  
        self.up_btn.pressed.connect(self.up_btn_pressed)
        self.up_btn.released.connect(self.up_btn_released)

        self.down_btn = QtWidgets.QPushButton("DOWN")
        self.down_btn.setIcon(QtGui.QIcon(os.getcwd()+"//images//down.png"))
        self.down_btn.setIconSize(QtCore.QSize(24,24))
        self.down_btn.setStyleSheet("QPushButton"
                                "{"
                                "background-color : #3ca59d;"
                                "font: bold 13px;"
                                "padding: 6px;" 
                                "border-radius: 10px;"
                                "}"
                                "QPushButton::pressed"
                                "{"
                                "background-color : red;"
                                "}"
                                )          
        self.down_btn.pressed.connect(self.down_btn_pressed)
        self.down_btn.released.connect(self.down_btn_released)
        bt_layout.addWidget(self.up_btn) 
        bt_layout.addWidget(self.stop_btn) 
        bt_layout.addWidget(self.down_btn) 
        # layout2.addWidget(self.lf_graphWidget)
        # layout2.addWidget(self.rf_graphWidget)
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        widget.autoFillBackground()
        widget.setStyleSheet("background-color: #ffffff;")
        self.setCentralWidget(widget)      

        pen = pg.mkPen(color=(255, 82, 0))
        pen.setWidth(2)

        while len(self.y_F7) != len(self.index) or len(self.y_F8) != len(self.index):
            pass
        self.data_line =  self.F7_graphWidget.plot(self.index, self.y_F7, pen=pen)
        self.data_line2 =  self.F8_graphWidget.plot(self.index, self.y_F8, pen=pen)

        # self.data_line3 = self.lf_graphWidget.plot(self.index, self.left_flag, pen=pen)
        # self.data_line4 = self.rf_graphWidget.plot(self.index, self.right_flag, pen=pen)
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.up_btn_timer =  QtCore.QTimer()
        self.up_btn_timer.setInterval(100)
        self.up_btn_timer.timeout.connect(self.send_up)

        self.down_btn_timer =  QtCore.QTimer()
        self.down_btn_timer.setInterval(100)
        self.down_btn_timer.timeout.connect(self.send_down)
        

    def update_plot_data(self):
        if len(self.y_F7) == len(self.index) and len(self.y_F8) == len(self.index):
            self.data_line.setData(self.index, self.y_F7)  # Update the data.   
            self.data_line2.setData(self.index, self.y_F8)  # Update the data. 
            # self.data_line3.setData(self.index, self.left_flag)
            # self.data_line4.setData(self.index, self.right_flag) 
        # print(len(self.index))
        # print(len(self.y_F7),len(self.y_F8),len(self.left_flag), len(self.right_flag))       
    def F7_value_change(self):
        F7_threshold = self.F7_thresholdWidget.value()
        print(F7_threshold)
    def F8_value_change(self):
        F8_threshold = self.F8_thresholdWidget.value()    
        print('F8 value:{}'.format(F8_threshold))

    def stop_clicked(self):
        self.stop = ~self.stop
        if self.stop == 0:
            self.timer.stop()
            self.stop_btn.setStyleSheet("QPushButton"
                                    "{"
                                    "background-color : red;"
                                    "font: bold 13px;"
                                    "padding: 6px;" 
                                    "border-radius: 10px;"
                                    "}"
                                    "QPushButton::pressed"
                                    "{"
                                    "background-color : red;"
                                    "}"
                                    ) 
        else:
            self.timer.start()
            self.stop_btn.setStyleSheet("QPushButton"
                                    "{"
                                    "background-color : #3ca59d;"
                                    "font: bold 13px;"
                                    "padding: 6px;" 
                                    "border-radius: 10px;"
                                    "}"
                                    "QPushButton::pressed"
                                    "{"
                                    "background-color : red;"
                                    "}"
                                    )            

    def up_btn_pressed(self):
        self.up_btn_timer.start()

    def up_btn_released(self):
        self.up_btn_timer.stop()

    def up_btn_clicked(self):
        # print("click up")
        self.command.append('3')
        if self.robo <= 49:
            self.robo += 1
            pixmap = QtGui.QPixmap(os.getcwd()+"//images//robo//robo (" + str(self.robo) +").png")
            pixmap = pixmap.scaled(430, 540, QtCore.Qt.KeepAspectRatio)
            self.label.setPixmap(pixmap)

    def down_btn_clicked(self):
        print("clicked down")
        if self.robo >2:
            self.robo -= 1
            pixmap = QtGui.QPixmap(os.getcwd()+"//images//robo//robo (" + str(self.robo) +").png")
            pixmap = pixmap.scaled(430, 540, QtCore.Qt.KeepAspectRatio)
            self.label.setPixmap(pixmap)
        # command.append('4')

    def send_up(self):
        self.command.append('6')
        if self.robo <= 49:
            self.robo += 1
            pixmap = QtGui.QPixmap(os.getcwd()+"//images//robo//robo (" + str(self.robo) +").png")
            pixmap = pixmap.scaled(430, 540, QtCore.Qt.KeepAspectRatio)
            self.label.setPixmap(pixmap)

    def down_btn_pressed(self):
        self.down_btn_timer.start()

    def down_btn_released(self):
        self.down_btn_timer.stop()

    def send_down(self):
        self.command.append('5')
        if self.robo >2:
            self.robo -= 1
            pixmap = QtGui.QPixmap(os.getcwd()+"//images//robo//robo (" + str(self.robo) +").png")
            pixmap = pixmap.scaled(430, 540, QtCore.Qt.KeepAspectRatio)
            self.label.setPixmap(pixmap)        

def main(data_F7, data_F8, index, left_flag, right_flag, command):
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(data_F7, data_F8, index, left_flag, right_flag, command)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    command =[]
    main(1,1,1,1,1,command)
    