import os, time
import pandas as pd
import numpy as np
import warnings
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from Crawl.buffett.logs.log_setup import *
warnings.simplefilter("ignore", UserWarning)



class GetPDF():
    def __init__(self,
                path_all_com = 'Crawl/buffett/docs/List_company_23052023 - Listing.csv',
                path_save = 'SAVE/Buffett/Data'):
        self.driver = webdriver.Edge()
        self.path_company = 'https://www.buffett-code.com/company'
        self.path_save = path_save
        self.path_all_com = path_all_com
        self.log_path = self.path_all_com.replace('.csv', '.log').replace('docs/', 'logs/')
    
    def get_data(self, link):
        '''
        Get data from link of company
        Input: link of company
        Output: BeautifulSoup of company
        '''
        self.driver.get(link)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        return soup
    
    def get_table(self,soup = "", id_company = 5486):
        '''
        Get table have link pdf in web
        Input: BeautifulSoup of company
        Output: table have link pdf in web
        '''
        print(f"{self.path_company}/{id_company}/library")
        soup = self.get_data(f"{self.path_company}/{id_company}/library")
        table = soup.find_all('table')
        return table
    
    def get_pdf_link(self,link_):
        '''
        Get download link pdf in web
        Input: link preview pdf file
        Output: link download pdf file
        '''
        self.driver.get(link_)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        arr = soup.find_all('a')
        for i in arr:
            if i["href"].find("pdf") != -1:
                return i["href"]
        return ""


    def create_link_df(self, 
                       table):
        '''
        Create dataframe have link pdf
        Input: table have infor of link pdf
        Output: dataframe have link pdf
        '''
        json_company = {}
        for id_year, tr_year in enumerate(table[0].find_all('tr')):
            json_company_quy = {}
            year = ''
            for id_quy, td_quy in enumerate(tr_year.find_all('td')):
                lst_text, lst_link = [], []
                for li in td_quy.find_all('li'):
                    if '決算短信' in li.text:
                        lst_text.append(li.text)
                        lst_link.append(f"https://www.buffett-code.com{li.find('a')['href']}")
                if id_quy != 0 and id_quy != 5:
                    json_company_quy[f'Time_Q{id_quy}'] = lst_text
                    json_company_quy[f'Link_Q{id_quy}'] = lst_link
                    json_company_quy[f'Link_pdf_Q{id_quy}'] = np.nan
                if td_quy['class'][0] == 'center':
                    year = td_quy.text
            if year != '':
                json_company[year] = json_company_quy.copy()

        df = pd.DataFrame(json_company).T.reset_index(drop=False)
        return df.rename(columns={'index': 'Year'})


    def make_folder(self, 
                    id_company:int):
        '''
        Make folder to save pdf
        Input: id company
        Output: None
        '''
        try:
            os.mkdir(f'{self.path_save}/{id_company}')
            os.mkdir(f'{self.path_save}/{id_company}/PDF')
            os.mkdir(f'{self.path_save}/{id_company}/docs')
        except:
            pass


    def save_check_point(self, 
                         id_company:int):
        '''
        Save check point to checklist file
        Input: id company
        Output: None
        '''
        if not os.path.exists(f'{self.path_save}/{id_company}/docs/link.csv'):
            table = self.get_table(id_company=id_company)
            df = self.create_link_df(table)
            df.to_csv(f'{self.path_save}/{id_company}/docs/link.csv', index=False)
            df_check = df.copy()
            for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
                df_check[f'download_{quy}'] = np.nan
            df_check.to_csv(f'{self.path_save}/{id_company}/docs/check.csv', index=False)
        else:
            df = pd.read_csv(f'{self.path_save}/{id_company}/docs/link.csv')
            for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
                df[f'Time_{quy}'] = df[f'Time_{quy}'].apply(lambda x: eval(x))
                df[f'Link_{quy}'] = df[f'Link_{quy}'].apply(lambda x: eval(x))
        self.df_company = df
        return df

    def get_download_pdf(self, 
                         id_company:int):
        '''
        Download pdf file from link pdf
        Input: id company
        Output: None
        '''
        df = self.df_company
        df_check = pd.read_csv(f'{self.path_save}/{id_company}/docs/check.csv')

        for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
            for id in df.index:
                if pd.isna(df_check[f'download_{quy}'][id]):
                    for id_link in range(len(df[f'Time_{quy}'][id])):
                        year_ = df[f'Year'][id]
                        link_preview = df[f'Link_{quy}'][id][id_link]
                        if not f'{self.path_company}' in link_preview:
                            msg = 'Nan'
                        else:
                            try:
                                link_pdf = self.get_pdf_link(link_preview)
                                name = df[f'Time_{quy}'][id][id_link].replace(' ', '').replace('/', '_')
                                response = requests.get(link_pdf)
                                with open(f'{self.path_save}/{id_company}/PDF/{year_}_{quy}_{name}.pdf', 'wb') as f:
                                    f.write(response.content)
                                msg = 'OK'
                            except:
                                msg = None
                        print(f'{self.path_save}/{id_company} - {year_} - {quy} - {id_link} - {msg} - {link_preview}')
                        df_check[f'download_{quy}'][id] = msg
                        df_check.to_csv(f'{self.path_save}/{id_company}/docs/check.csv', index=False)
                        time.sleep(30)


    def save_pdf(self, 
                 id_company:int):
        '''
        Save pdf
        Input: id company
        Output: None
        '''
        self.make_folder(id_company)
        self.save_check_point(id_company)
        self.get_download_pdf(id_company)

    def get_all_com(self):
        '''
        Get all company
        '''
        logging.basicConfig(filename=self.log_path, level=logging.INFO)
        lst_com = pd.read_csv(self.path_all_com)
        if 'check' not in lst_com.columns:
            lst_com['check'] = np.nan
        for i in lst_com.index:
            id_company = lst_com['Symbol'][i]
            check = lst_com['check'][i]
            if check != 'Done':
                try:
                    self.save_pdf(id_company=id_company)
                    msg = 'Done'
                    log_message(f'Successfully: ID {id_company}')
                except:
                    msg = 'False'
                    log_message(f'Failed: ID {id_company}')
                lst_com['check'][i] = msg
                lst_com.to_csv(self.path_all_com, index=False)
