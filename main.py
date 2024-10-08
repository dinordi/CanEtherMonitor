from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.uic import loadUi

from CanEther.drive_data import DriveDataPacket
from CanEther.network import parse_packet

from datetime import datetime
from collections import deque
import socket

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

MAX_ITERATIONS = 200

class MainWindow(QMainWindow):
    update_plot_signal = pyqtSignal(object)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("CanEtherMonitor")
        self.setGeometry(100, 100, 800, 600)
        loadUi("gui/CanEther.ui", self)
        
        # ComboBox for selecting index
        self.index_selector = QComboBox(self)
        self.index_selector.addItems(['0', '1', '2', '3'])
        self.index_selector.currentIndexChanged.connect(self.change_index)
        self.matlabView.addWidget(self.index_selector)

        # Initialize plot
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

        # Data lists
        self.time_series = deque(maxlen=MAX_ITERATIONS)
        self.rpm = deque(maxlen=MAX_ITERATIONS)
        self.amps = deque(maxlen=MAX_ITERATIONS)
        self.fettemp = deque(maxlen=MAX_ITERATIONS)

        # Plot lines
        self.rpm_line, = self.ax1.plot([], [], label="RPM", color='b')
        self.amps_line, = self.ax2.plot([], [], label="Amps", color='r')
        self.fettemp_line, = self.ax3.plot([], [], label="FET Temp", color='g')

        self.fig.legend(loc='upper left')
        self.ax1.xaxis.set_major_locator(MaxNLocator(nbins=8))

        # Set up UDP socket
        self.UDP_IP = "0.0.0.0"
        self.UDP_PORT = 5000
        self.SENDER_IP = "192.168.144.32"

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.sock.settimeout(1.0)  # Set a timeout of 1 second

        self.start_time = datetime.now()

        # Initialize index
        self.index = 0

        

        # Timer to periodically check for new data
        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_data)
        self.timer.start(50)  # Check for new data every 50 ms

    def change_index(self, index):
        self.index = index

    def receive_data(self):
        try:
            data, addr = self.sock.recvfrom(512)  # Buffer size is 512 bytes
            if addr[0] != self.SENDER_IP:
                return
            packet = parse_packet(data)
            if packet is not None:
                current_time = (datetime.now() - self.start_time).total_seconds()
                self.update_plot_signal.emit((current_time, packet.rpm[self.index], packet.amps[self.index], packet.fettemp[self.index]))
        except socket.timeout:
            pass

    def update_plot(self, data):
        current_time, rpm, amps, fettemp = data

        self.time_series.append(current_time)
        self.rpm.append(rpm)
        self.amps.append(amps)
        self.fettemp.append(fettemp)

        self.rpm_line.set_data(self.time_series, self.rpm)
        self.amps_line.set_data(self.time_series, self.amps)
        self.fettemp_line.set_data(self.time_series, self.fettemp)

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