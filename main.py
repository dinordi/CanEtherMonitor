import struct
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 5000    # Replace with the actual port used by CanEthernet

# Define the CanEthernetPacketXL header structure
HEADER_FORMAT = '<HHBH'  # Adjust according to the actual structure
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
print(f"Header size: {HEADER_SIZE}")
# Define the structure of your packet.
class DriveDataPacket:
    def __init__(self, node_id, amps, rpm, fettemp):
        self.node_id = node_id
        self.amps = amps
        self.rpm = rpm
        self.fettemp = fettemp

    def __str__(self):
        return f"Node ID: {self.node_id}, Amps: {self.amps}, RPM: {self.rpm}, FET Temp: {self.fettemp}"

# Define a function to unpack the packet.
def unpack_drive_data_packet(data):
    # The format string here corresponds to:
    # 1 byte for nodeId, 12 floats for amps, rpm, and fettemp (4 for each array).
    # node_id_format = "!B"
    floats_format_str = "<B12f"  # B = unsigned char (1 byte), f = float (4 bytes)
   
    # Unpack the Node ID
    # node_id = struct.unpack(node_id_format, data[:2])[0]

    # print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data[2:])}")
    # print(len(data[2:]))

    # Unpack the binary data.
    floats = struct.unpack(floats_format_str, data)
    print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
    
    # Extract the unpacked values.
    node_id = floats[0]
    amps = floats[1:5]  # 4 float values
    rpm = floats[5:9]   # 4 float values
    fettemp = floats[9:13]  # 4 float values
    
    # Create the DriveDataPacket object.
    packet = DriveDataPacket(node_id, amps, rpm, fettemp)
    
    return packet


def parse_packet(data):
    # print(f"Received data: {data}")
    
    # Unpack the header
    header = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    packet_id, packet_type, node_id, length = header[:4]
    if packet_type != 2 or packet_id != 12353:
        # print(f"Skipping packet type {packet_type}")
        return None
    print(f"Header: {header}")
    # print(f"Expected payload length: {length}")
    
    # Extract the payload
    payload = data[HEADER_SIZE:HEADER_SIZE + length]
    #print all the data in hex

    # print(f"Payload: {payload}")
    # print(f"Payload in hex: {payload.hex()}")
    packet = unpack_drive_data_packet(payload)
    return packet
    # print(f"Actual payload length: {len(payload)}")
    # print(f"Payload: {payload}")
    
    if packet_type == 2:  # Assuming 2 is the type for DriveDataPacket
        try:
            drive_data = struct.unpack(DRIVE_DATA_FORMAT, payload[:DRIVE_DATA_SIZE])
            # print(f"Drive data: {drive_data}")  
            payload_parsed = {
                # 'drive_id': drive_data[0],
                'amps': drive_data[0:4],
                'rpm': drive_data[4:8],
                'fet_temp': drive_data[8:12]
            }
            # print(f"Parsed drive data: {payload_parsed}")
        except struct.error as e:
            print(f"Error unpacking drive data: {e}")
            drive_data = payload
            print(f"Raw payload length: {len(payload)}")
            payload_parsed = None
    else:
        payload_parsed = None

    return {
        'packet_id': hex(packet_id),
        'packet_type': packet_type,
        'node_id': node_id,
        'length': length,
        'payload': payload,
        'parsed_payload': payload_parsed
    }

def main():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"Listening on {UDP_IP}:{UDP_PORT}")
    
    while True:
        data, addr = sock.recvfrom(512)  # Buffer size is 2048 bytes
        print(f"Received data in hex: {' '.join(f'{byte:02x}' for byte in data)}")
        if addr[0] != '192.168.2.28':
            continue
        packet = parse_packet(data)
        print(packet)

if __name__ == "__main__":
    main()