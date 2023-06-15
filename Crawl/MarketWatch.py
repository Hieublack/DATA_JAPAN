from .base import setup
from .base import URL_MARKETWATCH, PATH_SAVE, TIMELINE
import pandas as pd
from datetime import datetime





class MarketWatch(setup.Setup):
    def __init__(self, path_save= PATH_SAVE):
        super().__init__(type_tech = "Request", source = "MarketWatch")
        self.end_date= datetime.strptime(TIMELINE["END_DATE"], "%d/%M/%Y")
        self.month_date = datetime.strftime(self.end_date, "%M/%d")
        self.current_year = TIMELINE['CURRENT_YEAR']
        self.list_fields = ["Date", "Open", "High", "Low", "Close", "Volume"]
        self.URL_MARKETWATCH_CLOSE = URL_MARKETWATCH['PRICE_CLOSE']
        self.path_save = f"{path_save}/{self.source}"
        self.checkPathExistAndCreatePath()

    def getPriceCloseMarketWatch(self, symbol):
        '''
        create link request data by symbol and year then get table by pandas, concat table until done. Then, remove duplicate
        '''
        done = False
        df = pd.DataFrame(columns= self.list_fields)
        temp_year = int(self.current_year)
        while not done:
            d_start = self.month_date + f'/{temp_year-1}'
            d_end = self.month_date + f'/{temp_year}'
            link = self.URL_MARKETWATCH_CLOSE.replace("SYMBOL", symbol).replace('STARTDATE', d_start).replace('ENDDATE', d_end)
            df_i = pd.read_csv(link) 
            df = pd.concat([df, df_i]).reset_index(drop= True)
            if len(df_i) < 2: #dont have any new data
                done = True
            temp_year -= 1
        df = df.drop_duplicates(subset=['Date'])
        return df

    def getPriceCloseByListCompany(self, list_company)-> None:
        '''
        input: list company
        crawl close_price of each company in list_company
        '''
        for symbol in list_company:
            # print(symbol)
            df_price = self.getPriceCloseMarketWatch(symbol= symbol)
            self.saveDataFrameCSV(df_price, symbol)

#################DONE##############################















