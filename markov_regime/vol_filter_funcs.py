import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

from markov_regime import *

end = dt.datetime.today()
start = dt.datetime(end.year - 10, end.month, end.day)
ticker = "^GSPC"
frequency = "weekly"
price_type = "Adj Close"

def index_fix(dataframe, dataframe_index, regime_index):
    
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
    dataframe = dataframe[2:]
    
    #check that they start, end, and have the same length
    if min(dataframe_index) == min(regime_index) and max(dataframe_index) == max(regime_index) and len(dataframe_index) == len(regime_index):
        
        print("everything matches")
        print("[DATAFRAME] min:", min(dataframe_index), "max:", max(dataframe_index), "len:", len(dataframe_index))
        print("[REGIME] min:", min(regime_index), "max:", max(regime_index), "len:", len(regime_index))
        
    return dataframe

def normalize(corr, dataframe, price_type):
    
    #get low and high values
    low, high = min(dataframe[price_type]), max(dataframe[price_type])
    
    #normalize
    corr_norm = pd.Series([low + (high - low) * x for x in corr])
    
    #add in index for plotting
    corr_norm.index = dataframe.index
    
    
    return corr_norm

def get_indicator(dataframe, ticker, frequency, price_type):

    #get regimes
    regimes = TimeSeries(dataframe, ticker, frequency, price_type).get_regime_data()
    
    #make the inverted series
    regimes['inverted'] = 1 - regimes['low_variance']
    
    #get the correlation
    corr = regimes['medium_variance'].rolling(window = 2).corr(regimes['inverted'])
    
    #fix the index problem
    dataframe = index_fix(dataframe, dataframe.index, regimes.index)
    
    #normalize the corr
    corr_norm = normalize(corr, dataframe, price_type)
    
    #make an output dataframe with what we want
    output = pd.DataFrame()
    output['prices'] = dataframe[price_type]    
    output['indicator'] = corr_norm
    
    return output

def plot_indicator(dataframe, ticker, frequency, price_type):
    
    #get regimes
    regimes = TimeSeries(dataframe, ticker, frequency, price_type).get_regime_data()
    
    #make the inverted series
    regimes['inverted'] = 1 - regimes['low_variance']
    
    #get the correlation
    corr = regimes['medium_variance'].rolling(window = 2).corr(regimes['inverted'])
    
    #fix the index problem
    dataframe = index_fix(dataframe, dataframe.index, regimes.index)
    
    #normalize the corr
    corr_norm = normalize(corr, dataframe, price_type)
    
    #make an output dataframe with what we want
    output = pd.DataFrame()
    output['prices'] = dataframe[price_type]    
    output['indicator'] = corr_norm
    
    output.plot(figsize = (24,10))
    plt.title("Indicator Function with Price")
    plt.show()

df = Prices(start, end, ticker, price_type, frequency).getPrices()
plot_inverted_regimes(df, ticker, frequency, price_type)

