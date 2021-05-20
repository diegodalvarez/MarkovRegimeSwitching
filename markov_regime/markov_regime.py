import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import matplotlib.pyplot as plt

class Prices:
    
    def __init__(self, start, end, ticker, price_type, frequency):
        
        self.start = start
        self.end = end
        self.ticker = ticker
        self.price_type = price_type
        self.frequency = frequency
    
    def getPrices(self):
        
        if self.frequency == "daily":
            
            df = yf.download(self.ticker, self.start, self.end)[self.price_type].to_frame()
            return df
        
        if self.frequency == "weekly":
            
            df = yf.download(self.ticker, self.start, self.end, interval = "1wk")[self.price_type].to_frame()
            return df
        
        if self.frequency == "monthly":
            
            df = yf.download(self.ticker, self.start, self.end, interval = "1mo")[self.price_type].to_frame()
            return df        

class TimeSeries:

    def __init__(self, df, ticker, frequency, price_type):
        
        self.df = df
        self.ticker = ticker
        self.frequency = frequency
        self.price_type = price_type
        self.company_name = company_name = yf.Ticker(self.ticker).info['shortName']

        self.df['return'] = df[self.price_type].pct_change()
        self.df = self.df.dropna()
        
        
    def plot_smoothed_probability(self):
        
        print("smoothed_probability")
        fig, axs = plt.subplots(4, 1, figsize = (10, 20))
        
        series = self.df[self.price_type].pct_change().to_frame().dropna()
        mod_kns = sm.tsa.MarkovRegression(series, k_regimes=3, trend = 'nc', switching_variance = 'True')
        res_kns = mod_kns.fit()
        
        axs[0].plot(series)
        axs[0].set_title("{} ".format(self.frequency) + "{} ".format(self.company_name) + "return")
        
        axs[1].plot(res_kns.smoothed_marginal_probabilities[0])
        axs[1].set_title("Smoothed probability of a low-variance regime for {}".format(self.company_name) + " {} returns".format(self.frequency))
        
        axs[2].plot(res_kns.smoothed_marginal_probabilities[1])
        axs[2].set_title("Smoothed probability of a medium-variance regime for {}".format(self.company_name) + " {} returns".format(self.frequency))
        
        axs[3].plot(res_kns.smoothed_marginal_probabilities[2])
        axs[3].set_title("Smoothed probability of a high-variance regime for {}".format(self.company_name) + " {} returns".format(self.frequency))
        
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        
    
    def get_regime_data(self):
        
        series = self.df[self.price_type].pct_change().to_frame().dropna()
        output_df = pd.DataFrame()
        
        fig, axs = plt.subplots(4, 1, figsize = (10, 20))
        
        mod_kns = sm.tsa.MarkovRegression(series, k_regimes=3, trend = 'nc', switching_variance = 'True')
        res_kns = mod_kns.fit()
        
        output_df['low_varaince'] = res_kns.smoothed_marginal_probabilities[0]
        output_df['medium_variance'] = res_kns.smoothed_marginal_probabilities[1]
        output_df['hihg_variance'] = res_kns.smoothed_marginal_probabilities[2]
        
        return output_df
            
        
        
        










