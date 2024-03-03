
'''
  Assignment 3 - Python application
  Instructions
 
  Create a Python Application, that
     Reads JSON from API
     Inserts into RedisJSON
     Does some processing (3 outputs) such as (matplotlib charts, aggregation, search, ...)
  
  The Python Application should be 
     Using Python Classes (not plain scripting as shown in lecture notes)
     Should contain necessary DocString
     Should be aligned properly
     Code should be pushed to GitHUB Public Repo. (Not uploaded)
 
  Submit the following:
     Github URL
     Captur input/output as screenshots (should be clearly visible) and add it to Google DOC and share URL.
 
  Follow the URL guidelines (clickable, shared, no email notification)
 
  Just a friendly heads-up: for EACH little slip-up, like Python Classes, missing docstrings,
  uploading manually to Github or messy code alignment, url guidelines, you'll lose 5 points
'''

# API
# Obtaining data from polygon.io - API of stock data
# NOTE: I had to pip install polygon-api-client
# API requires Python 3.8 or greater

import sys
from PolygonIoAPIWrapper import PolygonIoAPIWrapper
import pandas as pd
from db_config import get_redis_connection
import json
from StockDataProcessing import StockDataProcessing

# what are we running?
print(sys.version)

polygonClient = PolygonIoAPIWrapper()
redis_connection = get_redis_connection()

#######################################################
# Data #1
# list aggregates - (each timespans - open, close, high)
lmt_aggregate_json = polygonClient.json_aggregates(ticker="LMT", timespan="day", from_="2023-01-01", to="2024-02-29")
#print(lmt_aggregate_json)
rtx_aggregate_json = polygonClient.json_aggregates(ticker="RTX", timespan="day", from_="2023-01-01", to="2024-02-29")
ba_aggregate_json = polygonClient.json_aggregates(ticker="BA", timespan="day", from_="2023-01-01", to="2024-02-29")
noc_aggregate_json = polygonClient.json_aggregates(ticker="NOC", timespan="day", from_="2023-01-01", to="2024-02-29")
gd_aggregate_json = polygonClient.json_aggregates(ticker="GD", timespan="day", from_="2023-01-01", to="2024-02-29")
lhx_aggregate_json = polygonClient.json_aggregates(ticker="LHX", timespan="day", from_="2023-01-01", to="2024-02-29")
hii_aggregate_json = polygonClient.json_aggregates(ticker="HII", timespan="day", from_="2023-01-01", to="2024-02-29")
ldos_aggregate_json = polygonClient.json_aggregates(ticker="LDOS", timespan="day", from_="2023-01-01", to="2024-02-29")


# insert JSON into redis
redis_connection.json().set('stocks:aggregate:lmt', '.', json.dumps(lmt_aggregate_json))
redis_connection.json().set('stocks:aggregate:rtx', '.', json.dumps(rtx_aggregate_json))
redis_connection.json().set('stocks:aggregate:ba', '.', json.dumps(ba_aggregate_json))
redis_connection.json().set('stocks:aggregate:noc', '.', json.dumps(noc_aggregate_json))
redis_connection.json().set('stocks:aggregate:gd', '.', json.dumps(gd_aggregate_json))
redis_connection.json().set('stocks:aggregate:lhx', '.', json.dumps(lhx_aggregate_json))
redis_connection.json().set('stocks:aggregate:hii', '.', json.dumps(hii_aggregate_json))
redis_connection.json().set('stocks:aggregate:ldos', '.', json.dumps(ldos_aggregate_json))

# Get JSON
json_data = redis_connection.json().get('stocks:aggregate:lmt')
data = json.loads(json_data)
#print(json_data)

#######################################################
# Data #2
# ticker snapshots
# tickers we are interested in - top US defense contractors
tickers = ["LMT", "RTX", "BA", "NOC", "GD", "LHX", "HII", "LDOS"]
defense_snapshots_json = polygonClient.json_snapshots(tickers)
#print(defense_snapshots_json)

# insert JSON into redis
redis_connection.json().set('stocks:snapshots', '.', json.dumps(defense_snapshots_json))

# Get JSON
json_data = redis_connection.json().get('stocks:snapshots')
data = json.loads(json_data)
#print(json_data)

#######################################################
# Data #3
# get biggest gainers
biggest_gainers_json = polygonClient.json_biggest_gainers()
#print(biggest_gainers_json)

# insert JSON into redis
redis_connection.json().set('stocks:gainers', '.', json.dumps(biggest_gainers_json))

# Get JSON
json_data = redis_connection.json().get('stocks:gainers')
data = json.loads(json_data)
#print(json_data)

#######################################################
# Data #4
# get biggest losers
biggest_losers_json = polygonClient.json_biggest_losers()
#print(biggest_losers_json)

# insert JSON into redis
redis_connection.json().set('stocks:losers', '.', json.dumps(biggest_losers_json))

# Get JSON
json_data = redis_connection.json().get('stocks:losers')
data = json.loads(json_data)
#print(json_data)

#######################################################
# Data #5
# get list of exchanges
exchanges_json = polygonClient.json_exchanges()
#print(exchanges_json)

# insert JSON into redis
redis_connection.json().set('exchanges', '.', json.dumps(exchanges_json))

# Get JSON
json_data = redis_connection.json().get('exchanges')
data = json.loads(json_data)
#print(json_data)

#######################################################
# Data #6
# can get conditions but not using it, just printing the data
polygonClient.print_conditions()

#######################################################
# Data #7
# print the news on a stock (again not using it)
polygonClient.print_news(ticker="LMT")

#######################################################
# Processing #1
# Using a heatmap to see how correlated stocks are
stockDataProcessing = StockDataProcessing()

comparison_matrix = []

# Get JSON and put each day's close data into a df
tickers = ["lmt", "rtx", "ba", "noc", "gd", "lhx", "hii", "ldos"]
for ticker in tickers:
    json_data = redis_connection.json().get('stocks:aggregate:'+ticker)
    data = json.loads(json.loads(json_data))

    df = pd.DataFrame(data, columns=["date", "close"])
    df["date"] = pd.to_datetime(df["date"], unit="ms")
    df.set_index("date", inplace=True)
    df.rename(columns={"close": ticker}, inplace=True)
    comparison_matrix.append(df)

comparison_matrix = pd.concat(comparison_matrix, axis=1)
daily_returns = comparison_matrix.pct_change().dropna()
correlation_matrix = daily_returns.corr()
print(correlation_matrix)

stockDataProcessing.plot_correlation_heatmap(correlation_matrix);

#######################################################
# Processing #2
# snapshot percent change
json_data = redis_connection.json().get('stocks:snapshots')

stockDataProcessing.snapshot_percent_change(json_data)

#######################################################
# Processing #3
# Using highcharts.com visualize the aggregates
# Get JSON for the aggregate placed in redis
json_data = redis_connection.json().get('stocks:aggregate:lmt')

stockDataProcessing.visualize_aggregates(json_data)

exit()

#get single snapshot
polygonClient.print_single_snapshot(ticker="LMT")


