from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

from CanEther.drive_data import DriveDataPacket

class DataTable(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        self.width = 4
        self.height = 5
        self.labels = []
        self.rowNames = ["", "RPM", "Amps", "FET Temperature"]
        self.columnNames = ["", "Wheel 1", "Wheel 2", "Wheel 3", "Wheel 4"]

        for i in range(self.width):
            row_labels = []
            for j in range(self.height):
                if i == 0:
                    label = QLabel(self.columnNames[j])
                elif j == 0:
                    label = QLabel(self.rowNames[i])
                else:
                    label = QLabel("0")
                self.layout.addWidget(label, i, j)
                row_labels.append(label)
            self.labels.append(row_labels)

    def update_table(self, packet: DriveDataPacket):
        """
        Update the table with new data from a DriveDataPacket.
        :param packet: A DriveDataPacket instance containing the new data.
        """
        print(packet)
        print(type(packet))
        data = {
            "RPM": packet.rpm,
            "Amps": packet.amps,
            "FET Temperature": packet.fettemp
        }
        
        for i, row_name in enumerate(self.rowNames[1:], start=1):
            if row_name in data:
                for j, value in enumerate(data[row_name], start=1):
                    self.labels[i][j].setText(str(value))
                    print(f"Updating {row_name} {j} to {value}")