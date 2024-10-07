import socket
import struct

# Constants
NODE_ID = 0x20
TARGET_IP = "192.168.2.16"  # Replace with the target IP address
TARGET_PORT = 5000          # Replace with the target port
SOURCE_IP = "192.168.2.28"  # The source IP address

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the source IP address
sock.bind((SOURCE_IP, 0))

# Construct the header
header_type = 0x3041
header_id = 0x02
payload_length = 1 + 12 * 4  # 1 byte + 12 floats (each float is 4 bytes)
header = struct.pack('<HHBH', header_type, header_id, NODE_ID, payload_length)

# Construct the payload
byte_value = 0x20
float_values = [-5.0, 0.0, 0.0, 0.0, 1800.0, 0.0, 0.0, 0.0, 15.5, 0.0, 0.0, 0.0]
payload = struct.pack('<B' + 'f' * 12, byte_value, *float_values)

# Combine header and payload
message = header + payload
from time import sleep

while True:
    sleep(0.1)
    # Send the message
    sock.sendto(message, (TARGET_IP, TARGET_PORT))

    print(f"Message sent from {SOURCE_IP} to {TARGET_IP}:{TARGET_PORT}")

