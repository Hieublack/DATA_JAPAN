from .base import setup
from .base import URL_MORNINGSTAR, PATH_SAVE, TIMELINE
import numpy as np
import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


class MorningStar(setup.Setup):
    def __init__(self, path_save= PATH_SAVE):
        super().__init__(type_tech = "Selenium", source = "MorningStar")
        self.start_date= datetime.strptime(TIMELINE["START_DATE"], "%d/%M/%Y")
        self.end_date= datetime.strptime(TIMELINE["END_DATE"], "%d/%M/%Y")
        self.URL_MORNING_STAR_DIVIDEND = URL_MORNINGSTAR["DIVIDENDCASH"]
        self.path_save = f"{path_save}/{self.source}"
        self.action = ActionChains(self.driver)
        self.checkPathExistAndCreatePath()

    def resetDriver(self):
        chrome_options = webdriver.ChromeOptions()
        # hide selemium's window
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--incognito")  # inprivate mode
        self.driver = webdriver.Chrome(options=chrome_options)

    def setupLink(self, symbol):
        '''
        create link to request
        '''
        return self.URL_MORNING_STAR_DIVIDEND.replace('SYMBOL', str(symbol))

    def getDividendBySymbol(self, symbol, WAITING_TIME = 10):
        '''
        get dividend by company code (symbol), return dataframe
        '''
        link_dividend = self.setupLink(symbol= symbol)
        self.requestLink(link= link_dividend)
        #get max period
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[2]/div/div/div[1]/div/button[8]')
        #click event
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[1]/div[2]/div[1]/button[2]')
        #click dividends
        self.clickSomethingByXPath(element_path='/html/body/div[11]/div/div/section/div[2]/form/fieldset/div[1]/div/label/span')
        #click splits*
        self.clickSomethingByXPath(element_path='/html/body/div[11]/div/div/section/div[2]/form/fieldset/div[3]/div/label/span')
        #frequency_element
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[2]/div/div/div[3]/label/div[2]/select')
        #frequency_element_daily
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[2]/div/div/div[3]/label/div[2]/select/option[1]')
        #table_botton
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[2]/div/div/div[4]/button')
        #overview_button
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[3]/div[2]/section/label/div[2]/select')
        #option_dividends
        self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[3]/div[2]/section/label/div[2]/select/option[6]')
        length_table = 0
        self.action.scroll_by_amount(0, 1000).perform()
        try:
            # choose_view
            self.clickSomethingByXPath(element_path='/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[3]/div[2]/div[3]/div/div[2]/div/label/div[2]/select')
            #show_all
            self.clickSomethingByXPath(element_path= '/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[3]/div[2]/div[3]/div/div[2]/div/label/div[2]/select/option[4]')
            self.action.scroll_by_amount(0, 1000).perform()
            check_length = self.findElementByXPath('/html/body/div[2]/div/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-chart/div/div/mwc-markets-chart/div/div/div[1]/div[3]/div[2]/div[3]/div/div[1]/div[3]')
            length_table = int(check_length.text.split(' ')[-1])
        except:
            pass
        time.sleep(0.5)
        table = pd.read_html(self.driver.page_source)[0]
        if len(table) < length_table:
            raise Exception('table length is not equal to table real length', len(table) , length_table)
        return table

    def getDividendsByListSymbol(self, list_symbol):
        '''
        get dividend by list of company code (symbol), save each dataframe dividends to csv file, return check list
        '''
        check_list = []
        check_len = []
        for i in range(len(list_symbol)):
            trial = 0
            check = True
            while trial < 3:
                try:
                    df = self.getDividendBySymbol(symbol= list_symbol[i])
                    check_list.append(1)
                    check_len.append(len(df))

                    self.saveDataFrameCSV(dataframe= df, file_name= list_symbol[i])
                    break
                except:
                    trial += 1
                    check = False
            if not check:
                check_list.append(0)
                check_len.append(-1)
        df_check = pd.DataFrame({'Symbol': list_symbol, 'Check': check_list, 'Len': check_len})
        return df_check

#################DONE##############################