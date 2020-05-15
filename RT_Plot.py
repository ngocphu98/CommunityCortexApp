from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
import time
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data_F7, data_F8, index, left_flag, right_flag, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.data_F7 = data_F7
        self.data_F8 = data_F8
        self.y_F7 = data_F7
        self.y_F8 = data_F8
        self.index = index
        self.left_flag = left_flag
        self.right_flag = right_flag

        layout1 = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        main_layout = QtWidgets.QVBoxLayout()
        self.F7_graphWidget = pg.PlotWidget()
        self.F8_graphWidget = pg.PlotWidget()
        # lf = left_flag
        # rf = right_flag
        self.lf_graphWidget = pg.PlotWidget()
        self.rf_graphWidget = pg.PlotWidget()
        
        self.F7_graphWidget.setBackground('#222831')
        self.F8_graphWidget.setBackground('#222831')
        self.lf_graphWidget.setBackground('#222831')
        self.rf_graphWidget.setBackground('#222831')

        layout1.addWidget(self.F7_graphWidget)
        layout1.addWidget(self.F8_graphWidget)
        layout2.addWidget(self.lf_graphWidget)
        layout2.addWidget(self.rf_graphWidget)
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)      

        pen = pg.mkPen(color=(255, 0, 0))
        while len(self.y_F7) != len(self.index) or len(self.y_F8) != len(self.index):
            pass
        self.data_line =  self.F7_graphWidget.plot(self.index, self.y_F7, pen=pen)
        self.data_line2 =  self.F8_graphWidget.plot(self.index, self.y_F8, pen=pen)

        self.data_line3 = self.lf_graphWidget.plot(self.index, self.left_flag, pen=pen)
        self.data_line4 = self.rf_graphWidget.plot(self.index, self.right_flag, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        
    def update_plot_data(self):
        if len(self.y_F7) == len(self.index) and len(self.y_F8) == len(self.index) and len(self.left_flag) == len(self.index) and len(self.left_flag) == len(self.index):
            self.data_line.setData(self.index, self.y_F7)  # Update the data.   
            self.data_line2.setData(self.index, self.y_F8)  # Update the data. 
            self.data_line3.setData(self.index, self.left_flag)
            self.data_line4.setData(self.index, self.right_flag) 
        # print(len(self.index))
        # print(len(self.y_F7),len(self.y_F8),len(self.left_flag), len(self.right_flag))       

def main(data_F7, data_F8, index, left_flag, right_flag):
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(data_F7, data_F8, index, left_flag, right_flag)
    w.show()
    sys.exit(app.exec_())

    
    