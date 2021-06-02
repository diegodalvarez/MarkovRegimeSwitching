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
        
        mod_kns = sm.tsa.MarkovRegression(series, k_regimes=3, trend = 'nc', switching_variance = 'True')
        res_kns = mod_kns.fit()
        
        output_df['low_variance'] = res_kns.smoothed_marginal_probabilities[0]
        output_df['medium_variance'] = res_kns.smoothed_marginal_probabilities[1]
        output_df['high_variance'] = res_kns.smoothed_marginal_probabilities[2]
        
        return output_df
    
    def index_fix(self, dataframe_index, regime_index):
        
        #make a bool variable to find which index is bigger
        dataframe_larger = False
        
        if len(dataframe_index) > len(regime_index):
            dataframe_larger = True
        
        #when dataframe larger is bigger
        if dataframe_larger == True:
            
            #we want to make a counter to keep track of the position
            counter = 0
            
            #we want to go through all of the dataframe indexes
            for i in dataframe_index:
                
                #then find where to make our cut
                if i == regime_index[0]:
                    
                    print("first matching date:",i)
                    print("counter:", counter)
                
                #when they don't match 
                else:
                    
                    #update counter, counter will keep track of where to cut
                    counter += 1
                    
        #boolean may seem unnecessary but it allows for future patches if the other index is larger
        
        #do the slicing
        self.df = self.df[2:]
        
        #check that they start, end, and have the same length
        if min(dataframe_index) == min(regime_index) and max(dataframe_index) == max(regime_index) and len(dataframe_index) == len(regime_index):
            
            print("everything matches")
            print("[DATAFRAME] min:", min(dataframe_index), "max:", max(dataframe_index), "len:", len(dataframe_index))
            print("[REGIME] min:", min(regime_index), "max:", max(regime_index), "len:", len(regime_index))
            
        return self.df
    
    def normalize(self, corr):
        
        #get low and high values
        low, high = min(self.df[self.price_type]), max(self.df[self.price_type])
        
        #normalize
        corr_norm = pd.Series([low + (high - low) * x for x in corr])
        
        #add in index for plotting
        corr_norm.index = self.df.index
        
        
        return corr_norm
    
    def get_indicator(self):
    
        #get regimes
        regimes = TimeSeries(self.df, self.ticker, self.frequency, self.price_type).get_regime_data()
        
        #make the inverted series
        regimes['inverted'] = 1 - regimes['low_variance']
        
        #get the correlation
        corr = regimes['medium_variance'].rolling(window = 2).corr(regimes['inverted'])
        
        #fix the index problem
        self.df = self.index_fix(self.df.index, regimes.index)
        
        #normalize the corr
        corr_norm = self.normalize(corr)
        
        #make an output dataframe with what we want
        output = pd.DataFrame()
        output['prices'] = self.df[self.price_type]    
        output['indicator'] = corr_norm
        
        return output
    
    def plot_indicator(self):
    
        #get regimes
        regimes = TimeSeries(self.df, self.ticker, self.frequency, self.price_type).get_regime_data()
        
        #make the inverted series
        regimes['inverted'] = 1 - regimes['low_variance']
        
        #get the correlation
        corr = regimes['medium_variance'].rolling(window = 2).corr(regimes['inverted'])
        
        #fix the index problem
        self.df = self.index_fix(self.df.index, regimes.index)
        
        #normalize the corr
        corr_norm = self.normalize(corr)
        
        #make an output dataframe with what we want
        output = pd.DataFrame()
        output['prices'] = self.df[self.price_type]    
        output['indicator'] = corr_norm

        output.plot(figsize = (24,10))
        plt.title("Indicator Function with Price")
        plt.show()
