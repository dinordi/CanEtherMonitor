import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QPushButton, QComboBox, QGridLayout, QFileDialog
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.uic import loadUi

from CanEther.drive_data import DriveDataPacket #Data packet
from CanEther.network import Network    #Network class
from CanEther.dataTable import DataTable    #Live data table
from CanEther.mplGraphs import rpmGraph, ampsGraph, wheelGraph  #Plotly graphs

from datetime import datetime   #For logging


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

        #Combobox for selecting plotly Theme
        self.theme_selector: QComboBox = self.comboTheme
        self.theme_selector.addItems(['plotly_white', 'plotly_dark', 'plotly', 'ggplot2', 'seaborn', 'simple_white', 'none'])
        self.theme_selector.currentIndexChanged.connect(self.change_theme)


        self.mtl_layout.addWidget(self.index_selector)

        self.wheelGraph = wheelGraph(self)
        self.rpmGraph = rpmGraph(self)
        self.ampsGraph = ampsGraph(self)

        self.setupTable()
        self.setupMPLGraphs()

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

    def setupMPLGraphs(self):
        self.mtl_layout.addWidget(self.wheelGraph.get_frame())
        self.rpmView.addWidget(self.rpmGraph.get_frame())
        self.ampsView.addWidget(self.ampsGraph.get_frame())

    def logger(self, packet):
        # Write to a file in csv per value per wheel
        with open(self.logfile, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')},{packet.rpm[0]},{packet.rpm[1]},{packet.rpm[2]},{packet.rpm[3]},{packet.amps[0]},{packet.amps[1]},{packet.amps[2]},{packet.amps[3]},{packet.fettemp[0]},{packet.fettemp[1]},{packet.fettemp[2]},{packet.fettemp[3]}\n")

    def plot_csv_select(self):
        # Select the CSV file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csv_file = file_name
            self.wheelGraph.update_graph(self.csv_file, (self.index+1))
            self.rpmGraph.update_graph(self.csv_file)
            self.ampsGraph.update_graph(self.csv_file)

    def change_index(self, index):
        self.index = index
        self.refresh_plot()
    
    def change_theme(self):
        self.rpmGraph.set_theme(self.theme_selector.currentText())
        self.ampsGraph.set_theme(self.theme_selector.currentText())
        self.wheelGraph.set_theme(self.theme_selector.currentText())
        self.refresh_plot()
    
    def refresh_plot(self):
        self.rpmGraph.update_graph(self.csv_file)
        self.ampsGraph.update_graph(self.csv_file)
        self.wheelGraph.update_graph(self.csv_file, (self.index+1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()