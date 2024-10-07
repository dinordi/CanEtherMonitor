

class DriveDataPacket:
    def __init__(self, node_id, amps, rpm, fettemp):
        self.node_id = node_id
        self.amps = amps
        self.rpm = rpm
        self.fettemp = fettemp

    def __str__(self):
        return f"Node ID: {self.node_id}, Amps: {self.amps}, RPM: {self.rpm}, FET Temp: {self.fettemp}"
