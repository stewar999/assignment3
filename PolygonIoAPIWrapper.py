import config
from polygon import RESTClient
from polygon.rest.models import TickerSnapshot
from polygon.rest.models import Agg
from polygon.rest.models import Exchange
from polygon.rest.models import TickerNews
import json

class PolygonIoAPIWrapper:
    '''PolygonIoAPIWrapper is a class that wraps around the polygon.io API
       It is primarily used to return data from most functions in JSON format
    '''
    
    def __init__(self):
        '''Constructor that reads in the API key from a config.py file
           and stores the polygon.io RESTClient in the client member variable
        '''
        
        # fill config.py with polygon.io API key
        self.polygon_io_key = config.PolygonKey
        print(self.polygon_io_key)
        
        # get the RESTCLient using my API key
        self.client = RESTClient(api_key=self.polygon_io_key)
 
    def json_aggregates(self, ticker, timespan, from_, to):
        '''Aggregates are used to show data (opening, closing, high, low) for a specific stock over a specified period of time
           Inputs:
              ticker - string containing a stock's ticker symbol
              timespan - string containing a timespan window (second, minute, hour, day, month)
              from_ - start time of the window in YYYY-MM-DD
              to - end time of the window in YYYY-MM-DD
           Returns:
              aggregate data in JSON format
        '''
        # list aggregates as bars
        aggs = []
        for a in self.client.list_aggs(ticker=ticker, multiplier=1, timespan=timespan, from_=from_, to=to):
            aggs.append(a)
        #print(aggs)
        
        data = []
        for agg in aggs:
            new_record = {
                "date": agg.timestamp,
                "open": agg.open,
                "high": agg.high,
                "low": agg.low,
                "close": agg.close,
                "volume": agg.volume,
                "vwap": agg.vwap,
                "transactions": agg.transactions
                }
            data.append(new_record)

        values = [[v for k, v in d.items()] for d in data]
        
        json_aggs = json.dumps(data)
        #print(json_aggs)
        
        return json_aggs
    
    def json_snapshots(self, tickers):
        '''Snapshots show the latest 2-day span of data for a list of stocks, specified by their tickers
           Inputs:
              tickers - list of strings containing stock tickers
           Returns:
              snapshot data for each stock in JSON format
        '''       
        # how to get all tickers
        #snapshot = self.client.get_snapshot_all("stocks")
        
        # just get snapshot of the stocks from the input tickers
        self.snapshot = self.client.get_snapshot_all("stocks", tickers)
        print(self.snapshot)
        
        data = []
        for snap in self.snapshot:
            new_record = {
                "ticker": snap.ticker,
                "todays_change_percent": snap.todays_change_percent,
                "todays_change": snap.todays_change,
                "updated": snap.updated,
                "day": [
                    {"open": snap.day.open, "high": snap.day.high, "low": snap.day.low, "close": snap.day.close, "volume": snap.day.volume, "vwap": snap.day.vwap}
                ],
                "min": [
                    {"accumulated_volume": snap.min.accumulated_volume, "open": snap.min.open, "high": snap.min.high, "low": snap.min.low, "close": snap.min.close, "volume": snap.min.volume, "vwap": snap.min.vwap, "timestamp": snap.min.timestamp, "transactions": snap.min.transactions}
                ],
                "prev_day": [
                    {"open": snap.prev_day.open, "high": snap.prev_day.high, "low": snap.prev_day.low, "close": snap.prev_day.close, "volume": snap.prev_day.volume, "vwap": snap.prev_day.vwap}
                ]
                }
            data.append(new_record)

        values = [[v for k, v in d.items()] for d in data]
        
        json_snap = json.dumps(data)
        print(json_snap)
        return json_snap
        
    def snapshot_percent_change(self):
        '''Helper function that displays all snapshot data - by ticker, the previous day's open and close values, with percent change
           Prerequisite: Must run json_snapshot() to use this function 
        '''     
        # crunch some numbers
        for item in self.snapshot:
            # verify this is an TickerSnapshot
            if isinstance(item, TickerSnapshot):
                # verify this is an Agg
                if isinstance(item.prev_day, Agg):
                    # verify data is good
                    if (isinstance(item.prev_day.open, float) or isinstance(item.prev_day.open, int)) and (isinstance(item.prev_day.close, float) or isinstance(item.prev_day.close, int)):
                        percent_change = ((item.prev_day.close - item.prev_day.open) / item.prev_day.open * 100)
                        print(
                            "{:<15}{:<15}{:<15}{:.2f} %".format(
                                item.ticker,
                                item.prev_day.open,
                                item.prev_day.close,
                                percent_change)
                        )

    def json_biggest_gainers(self):
        '''Snapshot data for today's 20 biggest gainers
           Inputs:
              tickers - list of strings containing stock tickers
           Returns:
              snapshot data for each stock in JSON format
        '''    
        gainers = self.client.get_snapshot_direction("stocks", "gainers")
        #print(gainers)
        
        # print ticker with % change
        #for gainer in gainers:
            # verify this is a TickerSnapshot
        #    if isinstance(gainer, TickerSnapshot):
                # verify this is a float
        #        if isinstance(gainer.todays_change_percent, float):
        #            print("{:<15}{:.2f} %".format(gainer.ticker, gainer.todays_change_percent))
        #print()
        
        data = []
        for snap in gainers:
            new_record = {
                "ticker": snap.ticker,
                "todays_change_percent": snap.todays_change_percent,
                "todays_change": snap.todays_change,
                "updated": snap.updated,
                "day": [
                    {"open": snap.day.open, "high": snap.day.high, "low": snap.day.low, "close": snap.day.close, "volume": snap.day.volume, "vwap": snap.day.vwap}
                ],
                "min": [
                    {"accumulated_volume": snap.min.accumulated_volume, "open": snap.min.open, "high": snap.min.high, "low": snap.min.low, "close": snap.min.close, "volume": snap.min.volume, "vwap": snap.min.vwap, "timestamp": snap.min.timestamp, "transactions": snap.min.transactions}
                ],
                "prev_day": [
                    {"open": snap.prev_day.open, "high": snap.prev_day.high, "low": snap.prev_day.low, "close": snap.prev_day.close, "volume": snap.prev_day.volume, "vwap": snap.prev_day.vwap}
                ]
                }
            data.append(new_record)

        values = [[v for k, v in d.items()] for d in data]
        
        json_snap = json.dumps(data)
        #print(json_snap)
        
        return json_snap

    def json_biggest_losers(self):
        '''Snapshot data for today's 20 biggest losers
           Inputs:
              tickers - list of strings containing stock tickers
           Returns:
              snapshot data for each stock in JSON format
        '''    
        losers = self.client.get_snapshot_direction("stocks", "losers")
        #print(losers)

        # print ticker with % change
        #for loser in losers:
            # verify this is a TickerSnapshot
        #    if isinstance(loser, TickerSnapshot):
                # verify this is a float
        #        if isinstance(loser.todays_change_percent, float):
        #            print("{:<15}{:.2f} %".format(loser.ticker, loser.todays_change_percent))
        #print()
        
        data = []
        for snap in losers:
            new_record = {
                "ticker": snap.ticker,
                "todays_change_percent": snap.todays_change_percent,
                "todays_change": snap.todays_change,
                "updated": snap.updated,
                "day": [
                    {"open": snap.day.open, "high": snap.day.high, "low": snap.day.low, "close": snap.day.close, "volume": snap.day.volume, "vwap": snap.day.vwap}
                ],
                "min": [
                    {"accumulated_volume": snap.min.accumulated_volume, "open": snap.min.open, "high": snap.min.high, "low": snap.min.low, "close": snap.min.close, "volume": snap.min.volume, "vwap": snap.min.vwap, "timestamp": snap.min.timestamp, "transactions": snap.min.transactions}
                ],
                "prev_day": [
                    {"open": snap.prev_day.open, "high": snap.prev_day.high, "low": snap.prev_day.low, "close": snap.prev_day.close, "volume": snap.prev_day.volume, "vwap": snap.prev_day.vwap}
                ]
                }
            data.append(new_record)

        values = [[v for k, v in d.items()] for d in data]
        
        json_snap = json.dumps(data)
        #print(json_snap)
        
        return json_snap
    
    def print_single_snapshot(self, ticker):
        '''Helper function that displays all snapshot data for single ticker
           Inputs:
              ticker - string containing a stock's ticker symbol
        '''     
        snappy = self.client.get_snapshot_ticker("stocks", ticker=ticker)
        print(snappy)
    
    def json_exchanges(self):
        '''List of all exchanges 
           Returns:
              exchange data in JSON format
        '''      
        exchanges = self.client.get_exchanges()
        print(exchanges)

        # loop over exchanges
        #for exchange in exchanges:
            # verify this is an exchange
        #    if isinstance(exchange, Exchange):
                # print exchange info
        #        print(
        #            "{:<15}{} ({})".format(
        #                exchange.asset_class, exchange.name, exchange.operating_mic
        #            )
        #        )
        
        data = []
        for exchange in exchanges:
            new_record = {
                "type": exchange.type,
                "asset_class": exchange.asset_class,
                "locale": exchange.locale,
                "name": exchange.name,
                "acronym": exchange.acronym,
                "mic": exchange.mic,
                "operating_mic": exchange.operating_mic,
                "participant_id": exchange.participant_id,
                "url": exchange.url
                }
            data.append(new_record)

        values = [[v for k, v in d.items()] for d in data]
        
        json_ex = json.dumps(data)
        #print(json_ex)
        
        return json_ex
                
    def print_conditions(self):
        '''List all conditions that polygon.io uses
        '''
        conditions = []
        for c in self.client.list_conditions(limit=1000):
            conditions.append(c)
        print(conditions)
                
    def print_news(self, ticker):
        '''Prints news articles for specific ticker sysmbol, with url and synposis, limiting to 1000 entries
           In addition, prints the most recent 20 articles titles
        '''
        news = []
        for n in self.client.list_ticker_news(ticker, order="desc", limit=1000):
            news.append(n)
        #print(news)

        # print date + title
        for index, item in enumerate(news):
            # verify this is news
            if isinstance(item, TickerNews):
                print("{:<25}{:<15}".format(item.published_utc, item.title))

            if index == 20:
                break
        
    