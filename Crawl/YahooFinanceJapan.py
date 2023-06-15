from .base import setup
from .base import URL_YAHOOFINANCEJP, PATH_SAVE, TIMELINE
import numpy as np
import pandas as pd
import time
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

class YahooFinanceJP(setup.Setup):
    def __init__(self, path_save= PATH_SAVE):
        super().__init__(type_tech = "Request", source = "YahooFinanceJP")
        self.start_date= datetime.strptime(TIMELINE["START_DATE"], "%d/%M/%Y")
        self.end_date= datetime.strptime(TIMELINE["END_DATE"], "%d/%M/%Y")
        self.URL_YAHOOFINANCEJP_CLOSE = URL_YAHOOFINANCEJP["PRICE_CLOSE"].replace("STARTDATE", datetime.strftime(self.start_date, "%Y%M%d")).replace("ENDDATE", datetime.strftime(self.end_date, "%Y%M%d"))
        self.path_save = f"{path_save}/{self.source}"
        self.checkPathExistAndCreatePath()

    def setupLink(self, symbol, page):
        '''
        create link to request
        '''
        return self.URL_YAHOOFINANCEJP_CLOSE.replace('SYMBOL', symbol).replace('PAGE', str(page))

    def getRequest(self, link, time_wait= 3):
        '''
        request by link until done (wait = False)
        if error, wait for time_wait seconds then request again until done
        '''
        wait = True
        while wait:
            try:
                html = requests.get(link)
                wait = False
            except:
                time.sleep(time_wait)
        return html
    
    def findTableSinglePage(self, page_source):
        '''
        get table from page_source (html)
        '''
        df = pd.read_html(page_source.text,flavor='bs4',attrs={"class":"_13C_m5Hx _1aNPcH77"})[0]
        return df
    
    def getPriceCloseYahooFinanceJapan(self, symbol):
        '''
        get dataframe price by company code (symbol), return dataframe
        '''
        df_all = pd.DataFrame()
        page = 1
        while True:
            url = self.setupLink(symbol= symbol, page= page)
            print(url)
            html = self.getRequest(link= url)
            try:
                df_single = self.findTableSinglePage(page_source= html)
                df_all = pd.concat([df_all, df_single]).reset_index(drop=True)
            except:
                break
            page += 1
        return df_all

    def getPriceCloseByListCompany(self, list_company)-> None:
        '''
        input: list company
        crawl close_price of each company in list_company
        '''
        for symbol in list_company:
            # print(symbol)
            df_price = self.getPriceCloseYahooFinanceJapan(symbol= symbol)
            self.saveDataFrameCSV(df_price, symbol)


#################DONE##############################