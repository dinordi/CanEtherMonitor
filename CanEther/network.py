import struct
import socket
from CanEther.drive_data import DriveDataPacket

from PyQt6.QtCore import QThread, QObject, pyqtSignal

UDP_IP = "0.0.0.0"
UDP_PORT = 5000    # Replace with the actual port used by CanEthernet

SENDER_IP = "192.168.144.32"

# Define the CanEthernetPacketXL header structure
HEADER_FORMAT = '<HHBH'  # Adjust according to the actual structure
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def unpack_drive_data_packet(data):
    # The format string here corresponds to:
    # 1 byte for nodeId, 12 floats for amps, rpm, and fettemp (4 for each array).

    payload_format_string = "<B12f"  # B = unsigned char (1 byte), f = float (4 bytes)
   
    # Unpack the binary data.
    floats = struct.unpack(payload_format_string, data)
    # print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
    
    # Extract the unpacked values.
    node_id = floats[0]
    amps = [round(f, 2) for f in floats[1:5]]  # 4 float values rounded to 2 decimals
    rpm = [round(f, 2) for f in floats[5:9]]   # 4 float values rounded to 2 decimals
    fettemp = [round(f, 2) for f in floats[9:13]]  # 4 float values rounded to 2 decimals

    # Create the DriveDataPacket object.
    packet = DriveDataPacket(node_id, amps, rpm, fettemp)
    
    return packet



def parse_packet(data):

    # Unpack the header
    header = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    packet_id, packet_type, node_id, length = header[:4]
    if packet_type != 6 or packet_id != 12353:
        return None
    
    # Extract the payload
    payload = data[HEADER_SIZE:HEADER_SIZE + length] 
    packet = unpack_drive_data_packet(payload)
    return packet
    
    
def monitor(main_window):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    # print(f"Listening on {UDP_IP}:{UDP_PORT}")
    last_update_delta = 0
    while True:
        data, addr = sock.recvfrom(512)  # Buffer size is 2048 bytes
        # print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
        if addr[0] != SENDER_IP:
            continue
        packet = parse_packet(data)
        print(packet)
        if packet is not None:
            if last_update_delta >= 1:
                last_update_delta = 0
                main_window.update_plot_signal.emit(packet)
            else:
                last_update_delta += 0.01
        # print("Plot signal emitted")

class NetworkWorker(QObject):
    packet_received = pyqtSignal(object)

    def __init__(self, sock, sender_ip, debug=False):
        super().__init__()
        self.sock = sock
        self.SENDER_IP = sender_ip
        self.debug = debug
        self.listening = False

    def start_listening(self):
        self.listening = True
        self.monitor()

    def stop_listening(self):
        self.listening = False

    def monitor(self):
        print(f"Listening on {self.sock.getsockname()[0]}:{self.sock.getsockname()[1]}")
        while self.listening:
            try:
                data, addr = self.sock.recvfrom(512)  # Buffer size is 512 bytes
                if addr[0] != self.SENDER_IP:
                    continue
                if self.debug:
                    print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
                packet = parse_packet(data)
                if packet is not None:
                    self.packet_received.emit(packet)  # Send packet to GUI
            except socket.timeout:
                pass

class Network:
    def __init__(self, sender_ip, pyqt_signal, UDP_PORT=5000, debug=False):
        self.SENDER_IP = sender_ip
        self.UDP_PORT = UDP_PORT
        self.UDP_IP = "0.0.0.0"
        self.debug = debug
        self.emit_signal = pyqt_signal

        # Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.sock.settimeout(1.0)  # Set a timeout of 1 second

        # Worker and thread
        self.worker = NetworkWorker(self.sock, self.SENDER_IP, self.debug)
        self.worker.packet_received.connect(self.emit_signal)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start_listening)

    def toggleListener(self, toggle: bool):
        if toggle:
            if not self.thread.isRunning():
                self.thread.start()
        else:
            self.worker.stop_listening()
            self.thread.quit()
            self.thread.wait()