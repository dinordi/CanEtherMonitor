# test/plotly.py
import plotly.graph_objs as go
import pandas as pd

def plot_rpm_graph(csv_file):
    df = pd.read_csv(csv_file, parse_dates=[0], header=None)
    df.columns = ['Timestamp', 'RPM1', 'RPM2', 'RPM3', 'RPM4', 'Amps1', 'Amps2', 'Amps3', 'Amps4', 'FETTemp1', 'FETTemp2', 'FETTemp3', 'FETTemp4']

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['RPM1'], mode='lines', name='RPM1'))
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['RPM2'], mode='lines', name='RPM2'))
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['RPM3'], mode='lines', name='RPM3'))
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['RPM4'], mode='lines', name='RPM4'))

    fig.update_layout(
        title='RPM Graph',
        xaxis_title='Time',
        yaxis_title='RPM',
        template='plotly_dark'
    )

    # fig.show()
    return fig