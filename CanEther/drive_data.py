import pandas as pd

class DriveDataPacket:
    def __init__(self, node_id, amps, rpm, fettemp):
        self.node_id = node_id
        self.amps = amps
        self.rpm = rpm
        self.fettemp = fettemp

    def __str__(self):
        return f"Node ID: {self.node_id}, Amps: {self.amps}, RPM: {self.rpm}, FET Temp: {self.fettemp}"

def filter_data_by_timestamp(df, min_timestamp, max_timestamp):
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        mask = (df['Timestamp'] >= min_timestamp) & (df['Timestamp'] <= max_timestamp)
        return df.loc[mask]

def read_log_csv(logfilename):
        # Read the CSV file into a DataFrame
        try:
            df = pd.read_csv(logfilename, parse_dates=[0], header=None)
        except:
            print("CSV empty")
            return None
        df.columns = ['Timestamp', 'RPM1', 'RPM2', 'RPM3', 'RPM4', 'Amps1', 'Amps2', 'Amps3', 'Amps4', 'FETTemp1', 'FETTemp2', 'FETTemp3', 'FETTemp4']
        return df