from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class CrawlListCompany():
    def __init__(self):
        self.link_investing = 'https://www.investing.com'
        self.link_list_com = 'https://www.investing.com/stock-screener/?sp=country::35|sector::a|industry::a|equityType::a|exchange::20%3EviewData.symbol;'
        self.EMAIL = 'thiensuofclass@gmail.com'
        self.PASSWORD = 'xuanphong2002'
        self.signIn()

    def signIn(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.link_investing)
        element = self.driver.find_element('xpath', '//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        if element.is_displayed():
            element.click()
            time.sleep(2)
            
        self.driver.find_element('xpath', '//*[@id="userAccount"]/div/a[1]').click()
        time.sleep(0.5)
        self.driver.find_element('id', 'loginFormUser_email').send_keys(self.EMAIL)
        time.sleep(0.5)
        self.driver.find_element('id', 'loginForm_password').send_keys(self.PASSWORD)
        time.sleep(0.5)
        self.driver.find_element('xpath', '//*[@id="signup"]/a').click()
        time.sleep(2)
  

    def getTable(self):
        soup = BeautifulSoup(
            self.driver.page_source, "html.parser", from_encoding="utf-8"
        )
        table = soup.find_all("table")
        for i in range(len(table)):
            df = pd.read_html(str(table[i]))[0]
            if len(df.columns) >= 8:
                return df
        return None
    
    def getListCompany(self):
        for i in range(1, 1000):
            self.driver.get(self.link_list_com + str(i))
            time.sleep(3)
            df_temp = self.getTable()
            if i == 1:
                df_concat = df_temp
            else:
                df_concat = pd.concat([df_concat, df_temp], axis=0)
                if self.driver.current_url == self.link_list_com + '1':
                    break
            print(i, df_concat.shape)

        df_concat.drop_duplicates(inplace=True)
        df_concat.to_csv('data.csv', index=False)
