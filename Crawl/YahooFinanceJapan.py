from .base import setup
from .base import URL_YAHOOFINANCEJP, PATH_SAVE, TIMELINE
import numpy as np
import pandas as pd
import time
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import os

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
    
    def getPriceCloseByListCompany(self, list_company)-> None:
        '''
        input: list company
        crawl close_price of each company in list_company, save dataframe price and return check list
        '''
        list_check = []
        for symbol in list_company:
            if os.path.exists(f'{self.path_save}/{symbol}.csv'):
                list_check.append(1)
                continue
            df_price, total_len_df_price = self.getPriceCloseYahooFinanceJapanSelenium(symbol= symbol)
            if len(df_price) > 0 and len(df_price) >= (total_len_df_price - 5):
                list_check.append(1)
                # print('Success: ', symbol, "---", len(df_price), '---', total_len_df_price)
                self.saveDataFrameCSV(df_price, symbol)
            else:
                list_check.append(0)
        df_check = pd.DataFrame({"SYMBOL": list_company, "CHECK": list_check})
        return df_check

    def getPriceCloseYahooFinanceJapanSelenium(self, symbol):
        '''
        get dataframe price by company code (symbol), return dataframe
        '''
        df_all = pd.DataFrame()
        url = self.setupLink(symbol= symbol, page= 1)
        count_failed = 0
        int_number_rows = 0
        while count_failed < 5:
            self.requestLink(link= url)
            try:
                number_row = self.driver.find_element(By.XPATH, '//*[@id="pagerbtm"]/p')
                int_number_rows = int(number_row.text[number_row.text.index('/')+1:-1])
                break
            except:
                self.driver.quit()
                self.resetDriver()
                time.sleep(1)
                count_failed += 1
        check_continue = True
        old_url = self.driver.current_url

        while check_continue:
            try_find_next_page = 0
            while try_find_next_page < 5:
                try:
                    next_page = self.findElementByXPath('//*[@id="pagerbtm"]/ul/li[7]/button')
                    break
                except:
                    try_find_next_page += 1
                    self.driver.refresh()
                    continue
            try:
                df_single = pd.read_html(self.driver.page_source,flavor='bs4',attrs={"class":"_13C_m5Hx _1aNPcH77"})[0]
                df_all = pd.concat([df_all, df_single]).reset_index(drop=True)
            except:
                # print(f"{symbol} 's data not exist, len_current_df: {len(df_all)}")
                break
            try:
                self.clickThenScroll(next_page)
            except:
                pass
            if self.driver.current_url == old_url:
                check_continue = False
                break
            else:
                old_url = self.driver.current_url
        if len(df_all) < int_number_rows - 7:       #độ trễ data là 7 ngày
            df_all = pd.DataFrame()
        return df_all, int_number_rows
    
    def getNumberRowSelenium(self, symbol):
        '''
        get dataframe price by company code (symbol), return dataframe
        '''
        url = self.setupLink(symbol= symbol, page= 1)
        count_failed = 0
        int_number_rows = 0
        while count_failed < 5:
            self.requestLink(link= url)
            try:
                number_row = self.driver.find_element(By.XPATH, '//*[@id="pagerbtm"]/p')
                int_number_rows = int(number_row.text[number_row.text.index('/')+1:-1])
                break
            except:
                self.driver.quit()
                self.resetDriver()
                time.sleep(1)
                count_failed += 1
        return int_number_rows
    
    def getInformationAllCompany(self, list_company):
        '''
        get dataframe information all company by list_company, return dataframe
        '''
        #create columns for dataframe
        self.requestLink(link= self.URL_YAHOOFINANCE_INFORMATION.replace('SYMBOL', '1333'))    #request 1 cty có trên sàn, để lấy list fields
        table = pd.read_html(self.driver.page_source,flavor='bs4',attrs={"class":"BIq9BZEd"})[0]
        columns_df = ['SYMBOL'] + list(table[0])
        df_all = pd.DataFrame(columns=columns_df)
        for symbol in list_company:
            self.requestLink(link= self.URL_YAHOOFINANCE_INFORMATION.replace('SYMBOL', str(symbol)))    #request 1 cty có trên sàn, để lấy list fields
            try:
                table_symbol = self.findElementByXPath(element_path= '//*[@id="profile"]/div/table')
                table_ = pd.read_html(self.driver.page_source,flavor='bs4',attrs={"class":"BIq9BZEd"})[0]
                df_i = pd.DataFrame(columns=["SYMBOL"] + list(table_[0]), data=[[symbol] + list(table_[1])])
                df_all = pd.concat([df_all, df_i]).reset_index(drop=True)
            except:
                list_data = [symbol] + ['nan']*len(columns_df[1:])
                df_i = pd.DataFrame(columns=columns_df, data=[list_data])
                df_all = pd.concat([df_all, df_i]).reset_index(drop=True)
            
        return df_all
    
#################DONE##############################