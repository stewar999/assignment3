import datetime
import http.server
import socketserver
import traceback
import json
import matplotlib.pyplot as plt
import seaborn as sns 
import pandas as pd

class StockDataProcessing:
    '''StockDataProcessing is a class that contains the functions used
       to process JSON data obtained from the Redis database
    '''
    
    def __init__(self):
        '''Constructor
        '''
        
    def visualize_aggregates(self, json_data):
        '''This function takes the json_data, aggregate data for a stock, and formats
           the data in a format expected by the Highcharts JavaScript library. 
           It creates a web server that serves an HTML page that includes a candlestick chart 
           of the json_data stock prices using Highcharts.The server listens on port 8887 and
           exits gracefully when a KeyboardInterrupt is received.
           Inputs:
              json_data - aggregate of a single stock over a timespan
        '''
        # Connect to http://localhost:8887 in your browser to view candlestick chart.
        PORT = 8887

        # https://www.highcharts.com/blog/products/stock/
        # JavaScript StockChart with Date-Time Axis
        html = """
        <!DOCTYPE HTML>
        <html>
        <head>

        <style>
        #container {
            height: 750px;
            min-width: 310px;
        }
        </style>

        <script src="https://code.highcharts.com/stock/highstock.js"></script>
        <script src="https://code.highcharts.com/stock/modules/data.js"></script>
        <script src="https://code.highcharts.com/stock/modules/exporting.js"></script>
        <script src="https://code.highcharts.com/stock/modules/accessibility.js"></script>

        <div id="container"></div>

        <script type="text/javascript">
        Highcharts.getJSON('/data', function (data) {
            // create the chart
            Highcharts.stockChart('container', {
                rangeSelector: {
                    selected: 1
                },

                title: {
                    text: 'Stock Price'
                },

                series: [{
                    type: 'candlestick',
                    name: 'Stock Price',
                    data: data
                }]
            });
        });
        </script>
        </head>
        <body>
        """
        
        data = json.loads(json.loads(json_data))
        values = [[v for k, v in d.items()] for d in data]

        class handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/data":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    json_data = json.dumps(values)
                    self.wfile.write(json_data.encode())
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(html.encode())

        # handle ctrl-c KeyboardInterrupt to exit the program gracefully
        try:
            while True:
                # run http server
                with socketserver.TCPServer(("", PORT), handler) as httpd:
                    print("serving at port", PORT)
                    httpd.serve_forever()
                pass
        except KeyboardInterrupt:
            print("\nExiting gracefully...")
            # traceback.print_exc()
            
    def plot_correlation_heatmap(self, correlation_matrix):
        '''Function to plot a seaborn heatmap
           Inputs:
              correlation_matrix - an NxN matrix where the values represent how correlated each row is to each column, 
                 with the diagonal filled in with 1s.
        '''
        plt.figure(figsize=(8, 8))
        ax = sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8})
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        plt.title("Correlation Matrix Heatmap", y=1.08)
        plt.show()
        
    def snapshot_percent_change(self, json_data):
        '''Helper function that shows percent change using snapshot data - by ticker, the previous day's open and close values, with percent change
           Inputs:
              json_data - snapshot data 
        '''     
        data = json.loads(json.loads(json_data))
        
        # create table with percent change for yesterday's market data
        for item in data:
            ticker = item.get('ticker')
            prev_day = item.get('prev_day')
            for day in prev_day:
                prev_day_close = day.get('close')
                prev_day_open = day.get('open')
            percent_change = ((prev_day_close - prev_day_open) / prev_day_open * 100)
            print(
                  "{:<15}{:<15}{:<15}{:.2f} %".format(
                      ticker,
                      prev_day_open,
                      prev_day_close,
                      percent_change)
                 )

        exit()