# from ibapi.client import EClient
# from ibapi.wrapper import EWrapper
# from ibapi.contract import Contract

# class IBApp (EWrapper, EClient):
#     def __init__(self):
#         EClient.__init__(self, self)
#         self.connected = False
#         self.historical_data = {}

#     def error(self, reqId, errorCode, errorString):
#         print(f'Error {reqId} {errorCode} {errorString}')

#     def historicalData(self, reqId, bar):
#         if reqId not in self.historicalData:
#             self.historical_data[reqId] = []
#         self.historical_data[reqId].append({
#             'date' : bar.date,
#             'open' : bar.open,
#             'close': bar.close,
#             'high': bar.high,
#             'low': bar.low,
#             'volume': bar.volume
#         })

#         def historicalDataEnd(self, reqId, start, end):
#             print(f"Historical data has been received for reqId {reqId}")

import yfinance as yf

def historicalData(ticker, start_date, end_date, interval='1d'):  
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    
    historical_data = {}
    historical_data[ticker] = []

    for index, row in data.iterrows():
        historical_data[ticker].append({
            'date': index.strftime('%Y-%m-%d'),
            'open': float(row['Open'][ticker]),
            'close': float(row['Close'][ticker]),
            'high': float(row['High'][ticker]),
            'low': float(row['Low'][ticker]),
            'volume': int(row['Volume'][ticker])
        })

    return historical_data


my_data = historicalData('NVDA', '2023-04-12', '2023-04-13')
print(my_data)