import struct
import socket
from CanEther.drive_data import DriveDataPacket


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
    amps = floats[1:5]  # 4 float values
    rpm = floats[5:9]   # 4 float values
    fettemp = floats[9:13]  # 4 float values
    
    # Create the DriveDataPacket object.
    packet = DriveDataPacket(node_id, amps, rpm, fettemp)
    
    return packet


def parse_packet(data):

    # Unpack the header
    header = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    packet_id, packet_type, node_id, length = header[:4]
    if packet_type != 2 or packet_id != 12353:
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