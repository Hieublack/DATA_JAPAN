from .base import setup
from .base import URL_MINKABU
import numpy as np
import pandas as pd
import time
import re
import requests
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from .base.URL import PATH_SAVE







class Minkabu(setup.Setup):

    def __init__(self, path_save= PATH_SAVE):
        super().__init__(type_tech = "Selenium", source = "Minkabu")
        self.URL_MINKABU_CLOSE = URL_MINKABU["PRICE_CLOSE"]
        self.path_save = f"{path_save}/Minkabu"

        self.checkPathExistAndCreatePath()

    def setupLink(self, symbol):
        '''
        create link to access
        '''
        return self.URL_MINKABU_CLOSE.replace("SYMBOL", symbol)
    
    def FindTable(self, table_id):
        '''
        find table by table_id
        '''
        soup = BeautifulSoup(self.driver.page_source, features= 'lxml')
        tables = soup.select_one(table_id)
        tables = pd.read_html(str(tables))
        return tables

    def getPriceCloseMikabu(self, symbol):
        '''
        get dataframe price by company code (symbol), return dataframe
        '''
        URL = self.setupLink(symbol)
        self.requestLink(link= URL, time= 5)
        try:
            show_more = self.findElementByXPath(element_path= '/html/body/div[1]/div[2]/div[3]/div[4]/div[1]/div[1]/div[3]/div[1]/div/div/p/a')
        except:
            show_more = self.findElementByXPath(element_path='/html/body/div[1]/div[2]/div[3]/div[4]/div[1]/div[1]/div[3]/div[2]/div/div/p/a')
        
        for id_try in range(2000):
            waiting = True
            c = 0
            done = False
            while waiting:
                try:
                    self.clickThenScroll(button= show_more)
                    waiting = False
                except:
                    c += 1
                    if c >50:
                        waiting = False
                        done = True
            if done:
                break
        table = self.FindTable(table_id= "#fourvalue_timeline")
        # self.driver.quit()
        return table[0]

    def getPriceCloseByListCompany(self, list_company)-> None:
        '''
        input: list company
        crawl close_price of each company in list_company
        '''
        for symbol in list_company:
            # print(symbol)
            df_price = self.getPriceCloseMikabu(symbol= symbol)
            self.saveDataFrameCSV(df_price, symbol)
        


