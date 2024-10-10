from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

import mplcursors
import numpy as np

from CanEther.drive_data import read_log_csv, filter_data_by_timestamp
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy

#Graph that shows RPM of all wheels
class rpmGraph:

    def __init__(self, mainWindow):
        self.frame = QFrame()
        self.layout = QHBoxLayout()
        self.frame.setLayout(self.layout)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.MainWindow = mainWindow

        self.setup_axes()

    def setup_axes(self):
        self.fig, self.ax1 = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        self.ax1.set_xlabel("Time (s)")

        self.ax1.set_ylabel("RPM1", color='b')
        self.ax1.tick_params(axis='y', labelcolor='b')

        self.ax2 = self.ax1.twinx()
        self.ax2.spines['right'].set_position(('outward', 60))
        self.ax2.set_ylabel("RPM2", color='r')
        self.ax2.tick_params(axis='y', labelcolor='r')

        self.ax3 = self.ax1.twinx()
        self.ax3.spines['right'].set_position(('outward', 120))
        self.ax3.set_ylabel("RPM3", color='g')
        self.ax3.tick_params(axis='y', labelcolor='g')

        self.ax4 = self.ax1.twinx()
        self.ax4.spines['right'].set_position(('outward', 180))
        self.ax4.set_ylabel("RPM4", color='y')
        self.ax4.tick_params(axis='y', labelcolor='y')

        self.ax1.set_ylim(-5000.0, 5000.0)
        self.ax2.set_ylim(-5000.0, 5000.0)
        self.ax3.set_ylim(-5000.0, 5000.0)
        self.ax4.set_ylim(-5000.0, 5000.0)

        # Adjust the layout to make room for the additional y-axes
        self.fig.subplots_adjust(right=0.75)
        self.ax2.spines['right'].set_position(('axes', 1.1))
        self.ax3.spines['right'].set_position(('axes', 1.2))
        self.ax4.spines['right'].set_position(('axes', 1.3))

        # Plot lines
        self.rpm1_line, = self.ax1.plot([], [], label="RPM1", color='b')
        self.rpm2_line, = self.ax2.plot([], [], label="RPM2", color='r')
        self.rpm3_line, = self.ax3.plot([], [], label="RPM3", color='g')
        self.rpm4_line, = self.ax4.plot([], [], label="RPM4", color='y')

        self.rpm1_dots = self.ax1.scatter([], [], color='b')
        self.rpm2_dots = self.ax2.scatter([], [], color='r')
        self.rpm3_dots = self.ax3.scatter([], [], color='g')
        self.rpm4_dots = self.ax4.scatter([], [], color='y')


        self.layout.addWidget(self.canvas)

        self.fig.legend(loc='upper left')
        self.ax1.xaxis.set_major_locator(MaxNLocator(nbins=8))

        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
        self.ax1.xaxis.set_minor_locator(mdates.SecondLocator(interval=10))

        # Enable mplcursors for hovering
        self.cursor_rpm1 = mplcursors.cursor(self.rpm1_dots, hover=True)
        self.cursor_rpm1.connect("add", lambda sel: sel.annotation.set_text(
            f'Time: {mdates.num2date(sel.target[0]).strftime("%H:%M:%S.%f")}\nRPM: {sel.target[1]:.2f}'))

        
    def update_graph(self, logfilename):
        data = self.get_data(logfilename)
        current_time, rpm1, rpm2, rpm3, rpm4 = data
        
        self.time_series = current_time
        self.rpm1_line.set_data(self.time_series, rpm1)
        self.rpm2_line.set_data(self.time_series, rpm2)
        self.rpm3_line.set_data(self.time_series, rpm3)
        self.rpm4_line.set_data(self.time_series, rpm4)

        self.rpm1_dots.set_offsets(np.c_[self.time_series, rpm1])
        self.rpm2_dots.set_offsets(np.c_[self.time_series, rpm2])
        self.rpm3_dots.set_offsets(np.c_[self.time_series, rpm3])
        self.rpm4_dots.set_offsets(np.c_[self.time_series, rpm4])


        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.ax4.relim()
        self.ax4.autoscale_view()

        self.fig.tight_layout()
        self.canvas.draw()

    def get_data(self, logfilename):
        df = read_log_csv(logfilename)
        if df is None:
            return
        min_timestamp = self.MainWindow.lineEdit_MinTime.text()
        max_timestamp = self.MainWindow.lineEdit_MaxTime.text()
        df = filter_data_by_timestamp(df, min_timestamp, max_timestamp)

        #TODO: clean this up
        time_series = df['Timestamp'].to_list()
        rpm1 = df['RPM1'].to_list()
        rpm2 = df['RPM2'].to_list()
        rpm3 = df['RPM3'].to_list()
        rpm4 = df['RPM4'].to_list()
            
        main_data = [time_series, rpm1, rpm2, rpm3, rpm4]
        return main_data
    
    def get_frame(self):
        return self.frame
    

#Graph that shows RPM of all wheels
class ampsGraph:

    def __init__(self, mainWindow):
        self.frame = QFrame()
        self.layout = QHBoxLayout()
        self.frame.setLayout(self.layout)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.MainWindow = mainWindow

        self.setup_axes()

    def setup_axes(self):
        self.fig, self.ax1 = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        self.ax1.set_xlabel("Time (s)")

        self.ax1.set_ylabel("AMPS1", color='b')
        self.ax1.tick_params(axis='y', labelcolor='b')

        self.ax2 = self.ax1.twinx()
        self.ax2.spines['right'].set_position(('outward', 60))
        self.ax2.set_ylabel("AMPS2", color='r')
        self.ax2.tick_params(axis='y', labelcolor='r')

        self.ax3 = self.ax1.twinx()
        self.ax3.spines['right'].set_position(('outward', 120))
        self.ax3.set_ylabel("AMPS3", color='g')
        self.ax3.tick_params(axis='y', labelcolor='g')

        self.ax4 = self.ax1.twinx()
        self.ax4.spines['right'].set_position(('outward', 180))
        self.ax4.set_ylabel("AMPS4", color='y')
        self.ax4.tick_params(axis='y', labelcolor='y')

        self.ax1.set_ylim(-50.0, 50.0)
        self.ax2.set_ylim(-50.0, 50.0)
        self.ax3.set_ylim(-50.0, 50.0)
        self.ax4.set_ylim(-50.0, 50.0)

        # Adjust the layout to make room for the additional y-axes
        self.fig.subplots_adjust(right=0.75)
        self.ax2.spines['right'].set_position(('axes', 1.1))
        self.ax3.spines['right'].set_position(('axes', 1.2))
        self.ax4.spines['right'].set_position(('axes', 1.3))

        # Plot lines
        self.amps1_line, = self.ax1.plot([], [], label="amps1", color='b')
        self.amps2_line, = self.ax2.plot([], [], label="amps2", color='r')
        self.amps3_line, = self.ax3.plot([], [], label="amps3", color='g')
        self.amps4_line, = self.ax4.plot([], [], label="amps4", color='y')

        self.amps1_dots = self.ax1.scatter([], [], color='b')
        self.amps2_dots = self.ax2.scatter([], [], color='r')
        self.amps3_dots = self.ax3.scatter([], [], color='g')
        self.amps4_dots = self.ax4.scatter([], [], color='y')


        self.layout.addWidget(self.canvas)

        self.fig.legend(loc='upper left')
        self.ax1.xaxis.set_major_locator(MaxNLocator(nbins=8))

        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
        self.ax1.xaxis.set_minor_locator(mdates.SecondLocator(interval=10))

        # Enable mplcursors for hovering
        self.cursor_amps1 = mplcursors.cursor(self.amps1_dots, hover=True)
        self.cursor_amps1.connect("add", lambda sel: sel.annotation.set_text(
            f'Time: {mdates.num2date(sel.target[0]).strftime("%H:%M:%S.%f")}\namps: {sel.target[1]:.2f}'))

        
    def update_graph(self, logfilename):
        data = self.get_data(logfilename)
        current_time, amps1, amps2, amps3, amps4 = data
        
        self.time_series = current_time
        self.amps1_line.set_data(self.time_series, amps1)
        self.amps2_line.set_data(self.time_series, amps2)
        self.amps3_line.set_data(self.time_series, amps3)
        self.amps4_line.set_data(self.time_series, amps4)

        self.amps1_dots.set_offsets(np.c_[self.time_series, amps1])
        self.amps2_dots.set_offsets(np.c_[self.time_series, amps2])
        self.amps3_dots.set_offsets(np.c_[self.time_series, amps3])
        self.amps4_dots.set_offsets(np.c_[self.time_series, amps4])


        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.ax4.relim()
        self.ax4.autoscale_view()

        self.fig.tight_layout()
        self.canvas.draw()

    def get_data(self, logfilename):
        df = read_log_csv(logfilename)
        if df is None:
            return
        min_timestamp = self.MainWindow.lineEdit_MinTime.text()
        max_timestamp = self.MainWindow.lineEdit_MaxTime.text()
        df = filter_data_by_timestamp(df, min_timestamp, max_timestamp)

        #TODO: clean this up
        time_series = df['Timestamp'].to_list()
        amps1 = df['Amps1'].to_list()
        amps2 = df['Amps2'].to_list()
        amps3 = df['Amps3'].to_list()
        amps4 = df['Amps4'].to_list()
            
        main_data = [time_series, amps1, amps2, amps3, amps4]
        return main_data
    
    def get_frame(self):
        return self.frame