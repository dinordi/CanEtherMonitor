import struct
import socket
from datetime import datetime

UDP_IP = "0.0.0.0"
UDP_PORT = 5000    # Replace with the actual port used by CanEthernet

SENDER_IP = "192.168.144.32"

# Define the CanEthernetPacketXL header structure
HEADER_FORMAT = '<HHBH'  # Adjust according to the actual structure
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)




class DriveDataPacket:
    def __init__(self, node_id, amps, rpm, fettemp):
        self.node_id = node_id
        self.amps = amps
        self.rpm = rpm
        self.fettemp = fettemp

    def __str__(self):
        return f"Node ID: {self.node_id}, Amps: {self.amps}, RPM: {self.rpm}, FET Temp: {self.fettemp}"


def unpack_drive_data_packet(data):
    # The format string here corresponds to:
    # 1 byte for nodeId, 12 floats for amps, rpm, and fettemp (4 for each array).

    payload_format_string = "<B12f"  # B = unsigned char (1 byte), f = float (4 bytes)
   
    # Unpack the binary data.
    floats = struct.unpack(payload_format_string, data)
    print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
    
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
    print(f"Header: {header}")
    
    # Extract the payload
    payload = data[HEADER_SIZE:HEADER_SIZE + length] 
    packet = unpack_drive_data_packet(payload)
    return packet

def logger(packet, logfile):
        # Write to a file in csv per value per wheel
        with open(logfile, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{packet.rpm[0]},{packet.rpm[1]},{packet.rpm[2]},{packet.rpm[3]},{packet.amps[0]},{packet.amps[1]},{packet.amps[2]},{packet.amps[3]},{packet.fettemp[0]},{packet.fettemp[1]},{packet.fettemp[2]},{packet.fettemp[3]}\n")

    
def main():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"Listening on {UDP_IP}:{UDP_PORT}")
    logfilename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    while True:
        data, addr = sock.recvfrom(512)  # Buffer size is 2048 bytes
        # print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
        if addr[0] != SENDER_IP:
            continue
        packet = parse_packet(data)
        if packet is not None:
            print(packet)
            logger(packet, logfilename)

if __name__ == "__main__":
    main()