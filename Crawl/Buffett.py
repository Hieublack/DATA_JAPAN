from selenium import webdriver
from selenium.webdriver.common.by import By
from .base import URL_BUFFETT, PATH_SAVE, TIMELINE
import pandas as pd
import time
class Buffet:
    def __init__(self, path_save= PATH_SAVE):
        super().__init__(type_tech = "Request", source = "Buffet")
        


    def crawlInfo(br, comp, folderPath):
        '''
        Crawl and create file info company

        Parameters
        ------- 
            br: browser (selenium): br = webdriver.Edge()
            comp: company
            folderPath: Path to folder stores company info files 
        -------

        '''


        br.get(f'https://www.buffett-code.com/company/{comp}/')

        # i+=1
        # if i%60 == 0:
        #     sleep(1500)
        time.sleep(60)

        if br.current_url == f'https://www.buffett-code.com/company/{comp}/':
            
            tables = []
            try:
                table_1 = br.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div[4]/div/div[2]/table')
                tables.append(table_1)
            except:
                print(comp, "  table 1")
            
            try:
                table_2 = br.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div[4]/div/div[5]/table')
                tables.append(table_2)
            except:
                print(comp, "  table 2")
            
            try:
                table_3 = br.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div[10]/div/div[2]/table')
                tables.append(table_3)
            except:
                print(comp, "  table 3")


            dfs = [['Type'],['Value']]
            for tb in tables:
                
                rows = tb.find_elements(By.XPATH, ".//tbody/tr")
                for row in range(1,len(rows)+1):
                    values = []
                    for col in range(1,3):
                        dfs[col-1].append(tb.find_element(By.XPATH, f".//tbody/tr[{row}]/td[{col}]").text)
            
        else:
            dfs = [['Type'],['Value']]

        df_1 = pd.DataFrame(dfs[0])
        df_2 = pd.DataFrame(dfs[1])

        df_ = pd.concat([df_1,df_2], axis = 1)
        df_.to_csv(f"{folderPath}/{comp}.csv", header = False ,index = False)
