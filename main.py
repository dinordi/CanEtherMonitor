from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.uic import loadUi

from CanEther.drive_data import DriveDataPacket
from CanEther.network import monitor

import threading
from datetime import datetime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

MAX_ITERATIONS = 100

class MainWindow(QMainWindow):
    update_plot_signal = pyqtSignal(DriveDataPacket)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("CanEtherMonitor")
        self.setGeometry(100, 100, 800, 600)
        loadUi("gui/CanEther.ui", self)
        
        # Make 2d plot with time on X axis and RPM on Y axis
        self.fig, self.ax1 = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("RPM", color='b')
        self.ax1.tick_params(axis='y', labelcolor='b')

        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel("Amps", color='r')
        self.ax2.tick_params(axis='y', labelcolor='r')

        self.ax3 = self.ax1.twinx()
        self.ax3.spines['right'].set_position(('outward', 60))
        self.ax3.set_ylabel("FET Temp", color='g')
        self.ax3.tick_params(axis='y', labelcolor='g')

        self.matlabView.addWidget(self.canvas)

        self.update_plot_signal.connect(self.update_plot)

        #Data lists
        self.time_series = []
        self.rpm = []
        self.amps = []
        self.fettemp = []

        # Plot lines
        self.rpm_line, = self.ax1.plot([], [], label="RPM")
        self.amps_line, = self.ax2.plot([], [], label="Amps", color='r')
        self.fettemp_line, = self.ax3.plot([], [], label="FET Temp", color='g')

        self.fig.legend(loc='upper left')
        self.ax1.xaxis.set_major_locator(MaxNLocator(nbins=10))


        # Start the monitor thread multithreaded
        self.monitor_thread = threading.Thread(target=monitor, args=(self,))
        self.monitor_thread.start()

        self.start_time = datetime.now()


    def update_plot(self, packet):
        current_time = (datetime.now() - self.start_time).total_seconds()
        self.time_series.append(current_time)
        self.rpm.append(packet.rpm[0])
        self.amps.append(packet.amps[0])
        self.fettemp.append(packet.fettemp[0])

        # Limit the number of data points to the last 100
        self.time_series = self.time_series[-MAX_ITERATIONS:]
        self.rpm = self.rpm[-MAX_ITERATIONS:]
        self.amps = self.amps[-MAX_ITERATIONS:]
        self.fettemp = self.fettemp[-MAX_ITERATIONS:]

        # Update plot data
        self.rpm_line.set_data(self.time_series, self.rpm)
        self.amps_line.set_data(self.time_series, self.amps)
        self.fettemp_line.set_data(self.time_series, self.fettemp)

        # Adjust the view limits
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax3.relim()
        self.ax3.autoscale_view()

        self.fig.tight_layout()
        self.canvas.draw()
        # print("Plot updated")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
