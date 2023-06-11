import numpy as np
import pandas as pd
import time
import os
import requests
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class Setup():
    def __init__(self, type_tech="Selenium", source="Minkabu") -> None:
        self.year = 0
        self.quater = 0
        self.day = 0
        self.form_data = {}
        self.source = source
        self.path_save = ""
        

        if type_tech == "Selenium":
            self.resetDriver()

    def turnOffDriver(self):
        try:
            self.driver.quit()
        except:
            pass

    def resetDriver(self):
        chrome_options = webdriver.ChromeOptions()
        # hide selemium's window
        chrome_options.add_argument("--headless")
        if self.source == "Minkabu":
            chrome_options.add_argument("--incognito")  # inprivate mode
            chrome_options.add_argument("--window-size=1920x1080")

        self.driver = webdriver.Chrome(options=chrome_options)

    def requestLink(self, link, time=10):
        '''
        request link and wait for time second, if error, quit and reset driver
        '''
        try:
            self.driver.set_page_load_timeout(time)
            self.driver.get(link)
        except:
            self.driver.quit()
            self.resetDriver()

    def format(self, time):  # hàm cũ, ko dùng thì xóa sau
        s = time.split("-")
        self.year = int(s[0])
        self.quater = int(s[1])//3+1
        self.day = int(s[2])
        return self.year, self.quater

    def findElementByXPath(self, element_path):
        '''
        find element by it's path 
        '''
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, element_path)))
        finally:
            pass
        return element

    def clickSomethingByXPath(self, element_path):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, element_path))
            )
            element.click()
        except:
            self.driver.refresh()
            pass

    def clickSomethingByID(self, element_ID):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, element_ID))
            )
            element.click()
        except:
            self.driver.refresh()
            pass

    def sendSomethingByID(self, id, element_ID):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, id))
            )
            element.send_keys(element_ID)
        except:
            pass

    def requestPost(self, url, data, cookie={}, headers={}):
        return requests.post(url, headers=headers, data=data, cookies=cookie)

    def clickThenScroll(self, button, time_sleep=0.1, scroll=200):
        '''
        click on button and wait for time_sleep second to load, then scroll screen 
        '''
        time.sleep(time_sleep)
        button.click()
        self.driver.execute_script(
            f"window.scrollTo(0, window.scrollY + {scroll})")

    def checkPathExistAndCreatePath(self):
        '''
        Check if the directory exists, if not, create a directory
        '''
        if os.path.exists(self.path_save):
            pass
        else:
            os.mkdir(self.path_save)

    def saveDataFrameCSV(self, dataframe, file_name):
        '''
        save dataframe to csv file
        '''
        try:
            dataframe.to_csv(f"{self.path_save}/{file_name}.csv", index= False)
        except:
            # raise Exception("Can't save file")
            print("Can't save file")
            pass

