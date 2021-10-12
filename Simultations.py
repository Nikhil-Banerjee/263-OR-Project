from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime


def groupStoreDemands(DemandData):
    '''
    Filter demand data by store type
    '''
    CountdownData = DemandData.filter(axis = 0, regex = "Countdown (?!Metro)")
    SpecialData = DemandData.filter(axis = 0, regex = "(Metro|FreshChoice|SuperValue)")

    return CountdownData, SpecialData

def groupDemands():
    '''
    
    '''
    data = pd.read_csv('WoolworthsDemands.csv')
    
    # Tidies the data by having 3 columns in dataframe: Store, Date and Demand.
    data = data.melt(id_vars = 'Store', var_name = 'Date', value_name = 'Demand')
    
    # Creates new column 'Day Type' which classifies days of the week into: weekday, saturday and sunday.
    data['Date'] = pd.to_datetime(data['Date'])
    data['Wday'] = data['Date'].dt.weekday
    data['Day Type'] = np.where(data['Wday'] <= 4, 'Week Day', 'Sunday')
    data['Day Type'] = np.where(data['Wday'] == 5, 'Saturday', data['Day Type'])


    # Creates new column 'Store Type' which classifies stores into 2 categories: Traditional and Special.
    # Special stores are all FreshChoice, SuperValue and Countdown Metro stores.
    # Traditional stores are all other countdown stores.
    data['Store Type'] = np.where(data['Store'].str.contains('Metro'), 'Special', 'Traditional')
    data['Store Type'] = np.where(data['Store'].str.contains('FreshChoice'), 'Special', data['Store Type'])
    data['Store Type'] = np.where(data['Store'].str.contains('SuperValue'), 'Special', data['Store Type'])

    return data
    

# def BootstrapDemand(StoreTypeData):
#     '''
#     Generates demand for different store types
#     '''
#     ?????
    
#     return Demand

# Load demand data
data = groupDemands()

# Set number 
Simulations = 1000

# Weekdays
    
# WeekdayRoutes = # read in optimal routes

ExpectedTimes = [0]*Simulations
CompletionTimes = [0]*Simulations

# for i in Simulations:
#     # Calculate uncertain demands for each store type
#     Countdown = BootstrapDemand(CountdownData)
#     Special = BootstrapDemand(SpecialData)

#     # Calculate times of each route 
    
#     ExpectedTimes[i] = 
#     CompletionTimes[i] = 

#     # if demand > truck capacity add route 

#     # routetime =



# Histograms
plt.hist(CompletionTimes, density=True, histtype='stepfilled', alpha=0.2)
plt.hist(ExpectedTimes, density=True, histtype='stepfilled', alpha=0.2)

# Average completion time
print("average completion time: ", np.mean(CompletionTimes))

# One sample t-test, with H0 = expected completion time.
print(stats.ttest_1samp(CompletionTimes, H0)) # change HO

# Percentile interval
CompletionTimes.sort()
print(CompletionTimes[25], " to ", CompletionTimes[975])

# Error rate
error = sum(np.greater(CompletionTimes, ExpectedTimes))/len(CompletionTimes)
print("error = ", error)