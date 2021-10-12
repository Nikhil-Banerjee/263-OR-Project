from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def alphaBetaFromAmB(a, m, b):
    # Taken from code by David L. Mueller
    #github dlmueller/PERT-Beta-Python
    first_numer_alpha = 2.0 * (b + 4 * m - 5 * a)
    first_numer_beta = 2.0 * (5 * b - 4 * m - a)
    first_denom = 3.0 * (b - a)
    second_numer = (m - a) * (b - m)
    second_denom = (b - a) ** 2
    second = (1 + 4 * (second_numer / second_denom))
    alpha = (first_numer_alpha / first_denom) * second
    beta = (first_numer_beta / first_denom) * second
    return alpha, beta

def groupDemands(DemandData):
    '''
    Filter demand data by store type
    '''
    CountdownData = DemandData.filter(axis = 0, regex = "Countdown (?!Metro)")
    SpecialData = DemandData.filter(axis = 0, regex = ??????)

    return CountdownData, SpecialData


def StoreDemand(StoreTypeData):
    '''
    Generates demand for different store types
    '''

    a = # Lowest bound
    b = # Upper bound
    m = # mode
    
    alpha, beta = alphaBetaFromAmB(a, m, b)
    location = a
    scale = b - a
    
    Demand = stats.beta.rvs(alpha, beta) * scale + location
    
    return Demand

# Load demand data
DemandData = pd.read_csv('WoolworthsDemands.csv', index_col=0)

# Group data by store type
CountdownData, SpecialData = groupDemands(DemandData)

Simulations = 1000

# Weekdays
    
WeekdayRoutes = #read in optimal routes

ExpectedTimes = [0]*Simulations
CompletionTimes = [0]*Simulations

for i in Simulations:
    # Calculate uncertain demands for each store type
    Countdown = StoreDemand(CountdownData)
    Special = StoreDemand(SpecialData)

    # Calculate times of each route 
    
    
    ExpectedTimes[i] = Path3
    CompletionTimes[i] = max(?????????)



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