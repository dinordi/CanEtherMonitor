import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from PyQt6.QtWidgets import QFrame, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView as QWeb

#Graph that shows RPM of all wheels
class rpmGraph:

    def __init__(self, mainWindow):
        self.frame = QFrame()
        self.layout = QHBoxLayout()
        self.frame.setLayout(self.layout)
        self.fig = None
        self.MainWindow = mainWindow
        self.browser = QWeb(self.MainWindow)
        self.layout.addWidget(self.browser)
        self.theme = 'plotly_white'

    def update_graph(self, logfilename):
        self.fig = self.get_fig(logfilename)
        plotly_html = self.fig.to_html(include_plotlyjs='cdn')
        
        # Use JavaScript to update the plot container without replacing the entire content
        js_script = """
            <script>
            document.getElementById('plot-container').innerHTML = '%s
        
        """ % plotly_html
        
        # Update the browser content with the JavaScript and Plotly plot
        self.browser.setHtml(js_script)
        
    def get_fig(self, logfilename):
        df = pd.read_csv(logfilename, parse_dates=[0], header=None)
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
            template=self.theme
        )

        return fig
    
    def get_frame(self):
        return self.frame
    
    def set_theme(self, theme):
        self.theme = theme
    

#Graph that shows RPM of all wheels
class ampsGraph:

    def __init__(self, mainWindow):
        self.frame = QFrame()
        self.layout = QHBoxLayout()
        self.frame.setLayout(self.layout)
        self.fig = None
        self.MainWindow = mainWindow
        self.browser = QWeb(self.MainWindow)
        self.layout.addWidget(self.browser)
        self.theme = 'plotly_white'

    def update_graph(self, logfilename):
        self.fig = self.get_fig(logfilename)
        plotly_html = self.fig.to_html(include_plotlyjs='cdn')
        
        # Use JavaScript to update the plot container without replacing the entire content
        js_script = """
            <script>
            document.getElementById('plot-container').innerHTML = '%s
        
        """ % plotly_html
        
        # Update the browser content with the JavaScript and Plotly plot
        self.browser.setHtml(js_script)
        
    def get_fig(self, logfilename):
        df = pd.read_csv(logfilename, parse_dates=[0], header=None)
        df.columns = ['Timestamp', 'RPM1', 'RPM2', 'RPM3', 'RPM4', 'Amps1', 'Amps2', 'Amps3', 'Amps4', 'FETTemp1', 'FETTemp2', 'FETTemp3', 'FETTemp4']

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Amps1'], mode='lines', name='Amps1'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Amps2'], mode='lines', name='Amps2'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Amps3'], mode='lines', name='Amps3'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Amps4'], mode='lines', name='Amps4'))

        fig.update_layout(
            title='Amps Graph',
            xaxis_title='Time',
            yaxis_title='Amps',
            template=self.theme
        )

        return fig
    
    def get_frame(self):
        return self.frame
    
    def set_theme(self, theme):
        self.theme = theme
    
class wheelGraph:

    def __init__(self, mainWindow):
        self.frame = QFrame()
        self.layout = QHBoxLayout()
        self.frame.setLayout(self.layout)
        self.fig = None
        self.MainWindow = mainWindow
        self.browser = QWeb(self.MainWindow)
        self.layout.addWidget(self.browser)
        self.theme = 'plotly_white'

    def update_graph(self, logfilename, wheel_num):
        self.fig = self.get_fig(logfilename, wheel_num)
        plotly_html = self.fig.to_html(include_plotlyjs='cdn')
        
        # Use JavaScript to update the plot container without replacing the entire content
        js_script = """
            <script>
            document.getElementById('plot-container').innerHTML = '%s
        
        """ % plotly_html
        
        # Update the browser content with the JavaScript and Plotly plot
        self.browser.setHtml(js_script)
    
    def get_fig(self, logfilename, wheel_num):
        df = pd.read_csv(logfilename, parse_dates=[0], header=None)
        df.columns = ['Timestamp', 'RPM1', 'RPM2', 'RPM3', 'RPM4', 'Amps1', 'Amps2', 'Amps3', 'Amps4', 'FETTemp1', 'FETTemp2', 'FETTemp3', 'FETTemp4']

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        rpm_col = 'RPM' + str(wheel_num)
        amps_col = 'Amps' + str(wheel_num)
        fettemp_col = 'FETTemp' + str(wheel_num)

        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df[rpm_col], mode='lines', name='RPM'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df[amps_col], mode='lines', name='Amps'), secondary_y=True)
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df[fettemp_col], mode='lines', name='FET Temp'), secondary_y=True)

        fig.update_layout(
            title='Wheel Graph',
            xaxis_title='Time',
            yaxis_title='RPM',
            yaxis2_title='Amps/FET Temp',
            template=self.theme
        )

        return fig
    
    def get_frame(self):
        return self.frame
    
    def set_theme(self, theme):
        self.theme = theme