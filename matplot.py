import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import RadioButtons
import numpy as np
from datetime import datetime
from collections import deque
import socket
from CanEther.network import parse_packet

# Parameters
max_points = 100  # Maximum number of points to display
update_interval = 50  # Update interval in milliseconds (20 times per second)


# Initialize data
time_series = deque(maxlen=max_points)
rpm_series = deque(maxlen=max_points)
amps_series = deque(maxlen=max_points)
fettemp_series = deque(maxlen=max_points)

# Initialize plot
fig, ax1 = plt.subplots()
plt.subplots_adjust(left=0.3, right=0.95, top=0.95, bottom=0.1)

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("RPM", color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.set_ylabel("Amps", color='r')
ax2.tick_params(axis='y', labelcolor='r')

ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))
ax3.set_ylabel("FET Temp", color='g')
ax3.tick_params(axis='y', labelcolor='g')

# Plot lines
rpm_line, = ax1.plot([], [], label="RPM", color='b')
amps_line, = ax2.plot([], [], label="Amps", color='r')
fettemp_line, = ax3.plot([], [], label="FET Temp", color='g')

fig.legend(loc='upper left')

# Set up UDP socket
UDP_IP = "0.0.0.0"
UDP_PORT = 5000
SENDER_IP = "192.168.144.32"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

start_time = datetime.now()

#Initialize index
index = 0

# Function to receive and parse incoming data
def receive_data():
    while True:
        data, addr = sock.recvfrom(512)  # Buffer size is 512 bytes
        if addr[0] != SENDER_IP:
            continue
        packet = parse_packet(data)
        if packet is not None:
            current_time = (datetime.now() - start_time).total_seconds()
            yield current_time, packet.rpm[index], packet.amps[index], packet.fettemp[index]

# Update function for animation
def update(data):
    current_time, rpm, amps, fettemp = data

    time_series.append(current_time)
    rpm_series.append(rpm)
    amps_series.append(amps)
    fettemp_series.append(fettemp)

    rpm_line.set_data(time_series, rpm_series)
    amps_line.set_data(time_series, amps_series)
    fettemp_line.set_data(time_series, fettemp_series)

    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()
    ax3.relim()
    ax3.autoscale_view()

    return rpm_line, amps_line, fettemp_line

def change_index(label):
    global index
    index = int(label)


ax_radio = plt.axes([0.05, 0.3, 0.15, 0.15], facecolor='lightgoldenrodyellow')
radio = RadioButtons(ax_radio, ('0', '1', '2', '3'))
radio.on_clicked(change_index)

# Create animation
ani = animation.FuncAnimation(fig, update, receive_data, interval=update_interval, blit=True, cache_frame_data=False)

# Show plot
plt.tight_layout()
plt.show()