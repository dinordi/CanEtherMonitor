from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QComboBox, QGridLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.uic import loadUi

from CanEther.drive_data import DriveDataPacket, read_log_csv, filter_data_by_timestamp
from CanEther.network import Network
from CanEther.dataTable import DataTable
from CanEther.mplGraphs import rpmGraph

from datetime import datetime
from collections import deque
import socket

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

import mplcursors

import pandas as pd
import numpy as np


MAX_ITERATIONS = 50

class MainWindow(QMainWindow):
    packet_receved_signal = pyqtSignal(DriveDataPacket)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("CanEtherMonitor")
        self.setGeometry(100, 100, 800, 600)
        loadUi("gui/CanEther.ui", self)

        self.LISTENING_IP = "192.168.144.32"
        self.network = Network(self.LISTENING_IP, self.packet_receved_signal)
        
        self.mtl_layout: QGridLayout = self.matlabView
        self.live_layout: QGridLayout = self.LiveView
        self.header_layout: QHBoxLayout = self.headerLayout

        csv_button: QPushButton = self.btn_csv
        csv_button.clicked.connect(self.plot_csv_select)
        
        self.listener_button: QPushButton = self.btn_listener
        self.listener_button.clicked.connect(self.toggleListener)
        self.listener_button.setText(f"Start Listening on IP: {self.LISTENING_IP}")

        # ComboBox for selecting index
        self.index_selector = QComboBox(self)
        self.index_selector.addItems(['0', '1', '2', '3'])
        self.index_selector.currentIndexChanged.connect(self.change_index)

        self.mtl_layout.addWidget(self.index_selector)

        self.rpmGraph = rpmGraph(self)

        self.setupTable()
        self.setupWheelMPL()

        self.setupRPMGraph()

        # Initialize index
        self.index = 0
        self.logfile = ""
        self.csv_file = ""

        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.activated.connect(self.refresh_plot)


    def toggleListener(self):
        text = self.listener_button.text()
        toggle = "Start" in text

        self.network.toggleListener(toggle)
        if toggle:  #Make new CSV file
            self.startTime = datetime.now()
            self.logfile = f"{self.startTime.strftime('%Y_%m_%d_%H_%M_%S')}.csv"
            with open(self.logfile, 'w') as f:
                f.write('')
            self.listener_button.setText(f"Stop Listening on IP: {self.LISTENING_IP}")
        else:
            self.listener_button.setText(f"Start Listening on IP: {self.LISTENING_IP}")

        try:
            self.packet_receved_signal.disconnect()
        except:
            pass
        self.packet_receved_signal.connect(self.handle_packet)

    def handle_packet(self, packet: DriveDataPacket):
        self.logger(packet)
        self.tableWidget.update_table(packet)

    def setupTable(self):
        self.tableWidget = DataTable()
        self.live_layout.addWidget(self.tableWidget)

    def setupWheelMPL(self):
        # Initialize plot
        self.fig, self.ax1 = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("RPM", color='b')
        self.ax1.set_ylim(-6000.0, 6000.0)
        self.ax1.tick_params(axis='y', labelcolor='b')

        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel("Amps", color='r')
        self.ax2.set_ylim(-50.0, 100.0)
        self.ax2.tick_params(axis='y', labelcolor='r')

        self.ax3 = self.ax1.twinx()
        self.ax3.spines['right'].set_position(('outward', 60))
        self.ax3.set_ylabel("FET Temp", color='g')
        self.ax3.set_ylim(0.0, 100.0)
        self.ax3.tick_params(axis='y', labelcolor='g')

        self.mtl_layout.addWidget(self.canvas)

        # Plot lines
        self.rpm_line, = self.ax1.plot([], [], label="RPM", color='b')
        self.amps_line, = self.ax2.plot([], [], label="Amps", color='r')
        self.fettemp_line, = self.ax3.plot([], [], label="FET Temp", color='g')

        self.rpm_dots = self.ax1.scatter([], [], color='b')
        self.amps_dots = self.ax2.scatter([], [], color='r')
        self.fettemp_dots = self.ax3.scatter([], [], color='g')

        self.fig.legend(loc='upper left')
        self.ax1.xaxis.set_major_locator(MaxNLocator(nbins=8))

        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
        self.ax1.xaxis.set_minor_locator(mdates.SecondLocator(interval=10))

        # Enable mplcursors for hovering
        self.cursor_rpm = mplcursors.cursor(self.rpm_dots, hover=True)
        self.cursor_rpm.connect("add", lambda sel: sel.annotation.set_text(
            f'Time: {mdates.num2date(sel.target[0]).strftime("%H:%M:%S.%f")}\nRPM: {sel.target[1]:.2f}'))

        self.cursor_amps = mplcursors.cursor(self.amps_dots, hover=True)
        self.cursor_amps.connect("add", lambda sel: sel.annotation.set_text(
            f'Time: {mdates.num2date(sel.target[0]).strftime("%H:%M:%S.%f")}\nAmps: {sel.target[1]:.2f}'))

        self.cursor_fettemp = mplcursors.cursor(self.fettemp_dots, hover=True)
        self.cursor_fettemp.connect("add", lambda sel: sel.annotation.set_text(
            f'Time: {mdates.num2date(sel.target[0]).strftime("%H:%M:%S.%f")}\nFET Temp: {sel.target[1]:.2f}'))
    
    def setupRPMGraph(self):
        self.rpmView.addWidget(self.rpmGraph.get_frame())

    def logger(self, packet):
        # Write to a file in csv per value per wheel
        with open(self.logfile, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')},{packet.rpm[0]},{packet.rpm[1]},{packet.rpm[2]},{packet.rpm[3]},{packet.amps[0]},{packet.amps[1]},{packet.amps[2]},{packet.amps[3]},{packet.fettemp[0]},{packet.fettemp[1]},{packet.fettemp[2]},{packet.fettemp[3]}\n")

    # def read_log_csv(self, logfilename):
    #     # Read the CSV file into a DataFrame
    #     try:
    #         df = pd.read_csv(logfilename, parse_dates=[0], header=None)
    #     except:
    #         print("CSV empty")
    #         return None
    #     df.columns = ['Timestamp', 'RPM1', 'RPM2', 'RPM3', 'RPM4', 'Amps1', 'Amps2', 'Amps3', 'Amps4', 'FETTemp1', 'FETTemp2', 'FETTemp3', 'FETTemp4']
    #     return df

    def get_timestamps(self, df) -> tuple:
        min_timestamp = df['Timestamp'].iloc[0]
        max_timestamp = df['Timestamp'].iloc[-1]
        

        print(min_timestamp, max_timestamp)
        return min_timestamp, max_timestamp

    

    def plot_csv_data(self, logfilename):
        df = read_log_csv(logfilename)
        if df is None:
            return
        min_timestamp = self.lineEdit_MinTime.text()
        max_timestamp = self.lineEdit_MaxTime.text()
        df = filter_data_by_timestamp(df, min_timestamp, max_timestamp)

        #TODO: clean this up
        time_series = df['Timestamp'].to_list()
        rpm1 = df['RPM1'].to_list()
        rpm2 = df['RPM2'].to_list()
        rpm3 = df['RPM3'].to_list()
        rpm4 = df['RPM4'].to_list()
        amps1 = df['Amps1'].to_list()
        amps2 = df['Amps2'].to_list()
        amps3 = df['Amps3'].to_list()
        amps4 = df['Amps4'].to_list()
        fettemp1 = df['FETTemp1'].to_list()
        fettemp2 = df['FETTemp2'].to_list()
        fettemp3 = df['FETTemp3'].to_list()
        fettemp4 = df['FETTemp4'].to_list()

        data1 = (time_series, rpm1, amps1, fettemp1)
        data2 = (time_series, rpm2, amps2, fettemp2)
        data3 = (time_series, rpm3, amps3, fettemp3)
        data4 = (time_series, rpm4, amps4, fettemp4)
            
        main_data = [data1, data2, data3, data4]
        self.update_plot(main_data[self.index])

    def plot_csv_select(self):
        # Select the CSV file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csv_file = file_name
            df = read_log_csv(file_name)
            min_timestamp, max_timestamp = self.get_timestamps(df)
            self.lineEdit_MinTime.setText(min_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.lineEdit_MaxTime.setText(max_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.plot_csv_data(file_name)
            self.rpmGraph.update_graph(self.csv_file)

    def change_index(self, index):
        self.index = index
        self.plot_csv_data(self.csv_file)
    
    def refresh_plot(self):
        self.plot_csv_data(self.csv_file)
        self.rpmGraph.update_graph(self.csv_file)

    def update_plot(self, data):
        current_time, rpm, amps, fettemp = data
        
        self.time_series = current_time
        self.rpm_line.set_data(self.time_series, rpm)
        self.amps_line.set_data(self.time_series, amps)
        self.fettemp_line.set_data(self.time_series, fettemp)

        self.rpm_dots.set_offsets(np.c_[self.time_series, rpm])
        self.amps_dots.set_offsets(np.c_[self.time_series, amps])
        self.fettemp_dots.set_offsets(np.c_[self.time_series, fettemp])


        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax3.relim()
        self.ax3.autoscale_view()

        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()