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

def groupWeekdayDemands(DemandData):
    
    ?????

def BootstrapDemand(StoreTypeData):
    '''
    Generates demand for different store types
    '''
    ?????
    
    return Demand

def RandomTraffic():


# Load demand data
DemandData = pd.read_csv('WoolworthsDemands.csv', index_col=0)

# Group data by store type
CountdownData, SpecialData = groupStoreDemands(DemandData)


Simulations = 1000

# Weekdays
    
WeekdayRoutes = #read in optimal routes

ExpectedTimes = [0]*Simulations
CompletionTimes = [0]*Simulations

for i in Simulations:
    # Calculate uncertain demands for each store type
    Countdown = BootstrapDemand(CountdownData)
    Special = BootstrapDemand(SpecialData)
    Traffic = 

    # Calculate times of each route 
    
    
    ExpectedTimes[i] = 
    CompletionTimes[i] = 



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