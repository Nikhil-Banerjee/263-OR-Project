from pulp.utilities import value
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import random
from routeFuncsNikhil import *


# def groupStoreDemands(DemandData):
#     '''
#     Filter demand data by store type
#     '''
#     CountdownData = DemandData.filter(axis = 0, regex = "Countdown (?!Metro)")
#     SpecialData = DemandData.filter(axis = 0, regex = "(Metro|FreshChoice|SuperValue)")

#     return CountdownData, SpecialData

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

def listStores():
    '''
    Returns list of stores and their type using WoolworthLocations.csv
    '''
    stores = pd.read_csv('WoolworthsLocations.csv')
    stores = stores[['Type','Store']]
    stores['Class'] = np.where(stores['Type'] =='Countdown Metro', 'Special', 'Traditional')
    stores['Class'] = np.where(stores['Type'] =='FreshChoice', 'Special', stores['Class'])
    stores['Class'] = np.where(stores['Type'] =='SuperValue', 'Special', stores['Class'])
    stores['Class'] = np.where(stores['Type'] =='Distribution Centre', 'Distribution Centre', stores['Class'])

    stores = pd.Series(index=stores['Store'], data = stores['Class'])

    return stores

def possibleDemands(data, StoreType, DayType):
    '''
    Extracts possible demands for a store type and weekday combination
    '''
    data = data.loc[data['Day Type'] == DayType]
    data = data.loc[data['Store Type'] == StoreType]

    return data


def BootstrapDemand(StoreTypeData):
    '''
    Generates random demand for different store types
    '''
    Demand = StoreTypeData(random.randint(0,len(StoreTypeData)-1))
    return Demand

def addRoute(Route, Demands):
    '''
    Creates a new route if simulated demand exceeds truck capacity 
    '''
    # Currently only generating new routes of length 1, which means you can assume demand/time constraints wont be exceeded (if they are, then the delivery is not possible on any route)
    newRoutes = [Route]
    time = np.inf
    while sum([Demands[node] for node in newRoutes[0]]) > 26:
        newRoutes.append('')
        for index in range(len(Route[1:])):
            if (calculateRouteTime(Route[1:index] + Route[index:]) + roundTripTime('Distribution Centre Auckland',Route[index])) < time:
                time = calculateRouteTime(Route[1:index] + Route[index:]) + roundTripTime('Distribution Centre Auckland', Route[index])
                newRoutes[0] = Route[1:index] + Route[index:]
                newRoutes[-1] = ['Distribution Centre Auckland', Route[index]]
        Route = newRoutes[0]
    
    return newRoutes
    # Potentially incorporate combineRoutes function here (maybe using a combinations iterator)

def combineRoutes(Routes, Demands):
    # Combines routes in the most efficient way if they can be combined
    RouteFullList=[]
    combinedRoute, time = twoArcInterchange(RouteFullList.append([[Routes[i][j] for j in Routes[i][1:]] for i in Routes]))
    if sum([Demands[node] for node in combinedRoute]) <= 26 & time <= 14400:
        return combinedRoute
    else:
        return Routes
    
if __name__ == "__main__":
    # Load demand data
    data = groupDemands()

    # Set number of simulations 
    Simulations = 1000
        
    #Read in route information
    with open('UsedWkDayRoutes.pkl', 'rb') as f:
        wkDayR = pickle.load(f)
    with open('UsedSatRoutes.pkl', 'rb') as f:
        satR = pickle.load(f)

    ##### WEEKDAYS SIMULATION ######

    CountdownData = possibleDemands(data, 'Traditional', 'Week Day')
    SpecialData = possibleDemands(data, 'Special', 'Week Day')

    # ExpectedTimes = [0]*Simulations
    # CompletionTimes = [0]*Simulations

    for i in range(Simulations):
        # Calculate uncertain demands for each store
        Demand = listStores()
        for node in range(len(Demand)):
            if (Demand.loc[node,'Class'] == "Traditional"):
                Demand.at[node] = BootstrapDemand(CountdownData)
            elif (Demand.loc[node,'Class'] == "Distribution Centre"):
                # add distribution centre with demand of 0
                Demand.at[node] = 0
            else:
                Demand.at[node] = BootstrapDemand(SpecialData)

        # Calculate demands of each route 
        for route in wkDayR:
            routeDemand = 0 # initialise demand
            for node in route:
                routeDemand = routeDemand + Demand[node]
            if (routeDemand > 26):
                addRoute()


        # ExpectedTimes[i] = 
        # CompletionTimes[i] = 

        # if demand on a route > truck capacity add route 

        # routetimes =

    ##### SATURDAYS SIMULATION #######

    CountdownData = possibleDemands(data, 'Traditional', 'Saturday')

    # Repeat simulation for saturdays

    # # Histograms
    # plt.hist(CompletionTimes, density=True, histtype='stepfilled', alpha=0.2)
    # plt.hist(ExpectedTimes, density=True, histtype='stepfilled', alpha=0.2)

    # # Average completion time
    # print("average completion time: ", np.mean(CompletionTimes))

    # # One sample t-test, with H0 = expected completion time.
    # print(stats.ttest_1samp(CompletionTimes, H0)) # change HO

    # # Percentile interval
    # CompletionTimes.sort()
    # print(CompletionTimes[25], " to ", CompletionTimes[975])

    # # Error rate
    # error = sum(np.greater(CompletionTimes, ExpectedTimes))/len(CompletionTimes)
    # print("error = ", error)
