import requests as rq
import json as js
import csv as cv
import io
import pandas as pd
from datetime import datetime
from typing import NoReturn
from typing import TypeVar
from matplotlib import pyplot as plt
import yfinance as yf

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")

# class for stock market analysis
class StockMarket:
    startDate = ''
    endDate = ''

    def __init__(self, startdate: datetime, enddate: datetime):
        self.startDate = startdate
        self.endDate = enddate

    @staticmethod
    def date_format(dt: datetime) -> str:
        """
        This method changes the format of a datetime object to the standard format
        accepted by NASDAQ API
        """
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def show_upward_trend(df: PandasDataFrame, start_dt: datetime, end_dt: datetime) -> NoReturn:
        """
        This method is used to show consecutive upward for a certain date range for a particular stock
        """
        trend_days = 0
        df_sorted = df.sort_index()
        close_list = [row for row in df_sorted["Close"]]
        for i in range(len(close_list)):
            if i <= len(close_list):
                if close_list[i] > close_list[i - 1] > close_list[i - 2] and (i - 1 >= 0 and
                                                                              i - 2 >= 0):
                    print(f"{close_list[i]} , {close_list[i - 1]} ,and {close_list[i - 2]}")
                    trend_days = trend_days + 1
        print(f"Total consecutive upward trend from {start_dt} to {end_dt} : {trend_days} days")

    @staticmethod
    def show_sma_5_days_opening(dft: PandasDataFrame, name: str) -> NoReturn:
        """
        This method is used to get the 5 days Simple Moving Coverage of the closing price and
        compare it with the opening price of the date where opening price is higher than the said
        SMA
        """
        # to store the price percentage change in another data frame
        price_percentage = pd.Series([]) 
        dft.set_index('Date')
        dft['5 Days SMA Closing'] = dft.Close.rolling(window=5).mean()
        new_dft = dft[['Date', 'Open', '5 Days SMA Closing']]
        for i in new_dft.index:
            if new_dft["Open"][i] > new_dft["5 Days SMA Closing"][i]:
                price_change_percentage = ((new_dft["Open"][i] - new_dft["5 Days SMA Closing"][i]) /
                                           new_dft["5 Days SMA Closing"][i]) * 100
                # new_dft["price_change_percentage"][i] = price_change_percentage
                price_percentage[i] = price_change_percentage
                trading_date = new_dft["Date"][i]
                opening_amt = new_dft["Open"][i]
                sma_closing_amt = new_dft["5 Days SMA Closing"][i]
        # new data frame created with columns 'Date','Open','5 Days SMA Closing', 'price_change_percentage"
        new_dft.insert(3, "price_change_percentage", price_percentage)
        new_dft.sort_values(by=['price_change_percentage'], inplace=True)
        print(new_dft)

    def get_data(self, dt1: datetime, dt2: datetime, opt: int, stkname: str) -> NoReturn:
        """
        This method takes date range as input and calls the NASDAQ API and also creates the dataframe
        on the fly for further manipulation
        """
        date01 = self.date_format(dt1)
        date02 = self.date_format(dt2)

        try:
            # download the data in data frame format directly using yfinance module based on date range
            data = yf.download(stkname, start=date01, end=date02)
            # Reset the index of the dataframe
            data.reset_index(inplace=True, drop=False)
            print(f"Actual Dataset \n {data}")
            # data.plot()
            # plt.show()
        except ValueError as v:
            raise Exception("Error in fetching data due to {v}")

        if opt == 1:
            print("********* Consecutive Upward Trend *********")
            self.show_upward_trend(data, date01, date02)
        # elif opt == 2:
        # self.get_highest_trading_with_stock(data, date01, date02)
        elif opt == 3:
            self.show_sma_5_days_opening(data, stkname)
        else:
            print("Bad Option")
            exit(0)
     


if __name__ == '__main__':
    start_date = input('Enter Start Date. Date should be like this YYYY,MM,DD:')
    end_date = input('Enter End Date. Date should be like this YYYY,MM,DD:')
    stock_name = input("Enter Stock Name")
    option = int(input("Enter your option \n Press 1 for Consecutive Upward Trend"
                       "\n Press 2 for Highest Trading Volume and Significant Stock Price"
                       "\n Press 3 for Best Opening Price for 5 days "
                       "\n"))

    year1, month1, date1 = map(int, start_date.split(','))
    year2, month2, date2 = map(int, end_date.split(','))
    st_dt = datetime(year1, month1, date1)
    ed_dt = datetime(year2, month2, date2)
    stock = StockMarket(st_dt, ed_dt)
    stock.get_data(st_dt, ed_dt, option, stock_name)
