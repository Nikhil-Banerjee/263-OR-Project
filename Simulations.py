from pulp.utilities import value
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import random
from routeFuncsNikhil import *
from TrafficDistributionFunctions import *
from trafficSimulations import calcCost


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
    # Read in woolworths locations
    stores = pd.read_csv('WoolworthsLocations.csv')
    stores = stores[['Type','Store']]
    # set store class based on type
    stores['Class'] = np.where(stores['Type'] =='Countdown Metro', 'Special', 'Traditional')
    stores['Class'] = np.where(stores['Type'] =='FreshChoice', 'Special', stores['Class'])
    stores['Class'] = np.where(stores['Type'] =='SuperValue', 'Special', stores['Class'])
    stores['Class'] = np.where(stores['Type'] =='Distribution Centre', 'Distribution Centre', stores['Class'])
    stores = stores[['Store','Class']]
    stores = stores.set_index('Store')

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
    # choose random index
    ran = random.randint(0,len(StoreTypeData)-1)
    # select demand at random index
    Demand = StoreTypeData.iloc[ran]['Demand']
    return Demand

def addRoute(Route, Demands):
    '''
    Creates a new route if simulated demand exceeds truck capacity 
    '''
    # Currently only generating new routes of length 1, which means you can assume demand/time constraints wont be exceeded (if they are, then the delivery is not possible on any route)
    newRoutes = [Route]
    time = np.inf
    while sum([Demands.loc[node]['Class'] for node in newRoutes[0]]) > 26:
        newRoutes.append('')
        for index in range(len(Route[1:])):
            if (calculateRouteTime(Route[1:index] + Route[index+1:]) + roundTripTime('Distribution Centre Auckland',Route[index])) < time:
                time = calculateRouteTime(Route[1:index] + Route[index+1:]) + roundTripTime('Distribution Centre Auckland', Route[index])
                newRoutes[0] = Route[1:index] + Route[index+1:]
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

# def simulateWkDay(simulationsArray, data, wkDayR, satR, congestion, ):

#     pass

    
if __name__ == "__main__":
    # Load demand data
    data = groupDemands()

    np.random.seed(1)

    # Set number of simulations 
    Simulations = 100
        
    #Read in route information
    with open('UsedWkDayRoutes.pkl', 'rb') as f:
        wkDayR = pickle.load(f)
    with open('UsedSatRoutes.pkl', 'rb') as f:
        satR = pickle.load(f)

    
    congestion = pd.read_csv('AKL_congestion.csv', index_col=0)

    ##### WEEKDAYS SIMULATION ######
    weekday_8am = (congestion[["8am","9am","10am","11am"]]).loc["Mon":"Fri"]
    weekday_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Mon":"Fri"]

    CountdownData = possibleDemands(data, 'Traditional', 'Week Day')
    SpecialData = possibleDemands(data, 'Special', 'Week Day')

    WeekdayCost = [0]*Simulations

    initialDemand = listStores()
    

    # Each Simulation
    for i in range(Simulations):

        Demand = initialDemand

        # Calculate uncertain demands for each store
        for node in Demand.index:
            if (Demand.loc[node,'Class'] == "Traditional"):
                Demand.at[node] = BootstrapDemand(CountdownData)
            elif (Demand.loc[node,'Class'] == "Distribution Centre"):
                # add distribution centre with demand of 0
                Demand.at[node] = 0
            else:
                Demand.at[node] = BootstrapDemand(SpecialData)
        
        routes = wkDayR
        for route in routes:
            # if demand on a route > truck capacity add a new route 
            if (sum([Demand.loc[node]['Class'] for node in route]) > 26):
                newRoutes = addRoute(route, Demand)
                routes.remove(route)
                for j in newRoutes:
                    routes.append(j)
                    
        # Calculate the total time taken by each route (in minutes)
        totalRouteTime = np.zeros(len(routes))
        for ind in range(len(routes)):
            totalRouteTime[ind] = (sum([Demand.loc[node]['Class'] for node in routes[ind]])*7.5 + calculateRouteTime(route)/60)
        
        # Traffic effect
        if (len(totalRouteTime) <= 30):
            aMorn = findmin(weekday_8am.to_numpy())
            bMorn = findavg(weekday_8am.to_numpy())
            cMorn = findmax(weekday_8am.to_numpy())

            trafficMultiplierMorn = pert(aMorn,bMorn,cMorn)/100 + 1

            newTimes = totalRouteTime*trafficMultiplierMorn

        else:
            aMorn = findmin(weekday_8am.to_numpy())
            bMorn = findavg(weekday_8am.to_numpy())
            cMorn = findmax(weekday_8am.to_numpy())
            trafficMultiplierMorn = pert(aMorn,bMorn,cMorn)/100 + 1


            aAft = findmin(weekday_2pm.to_numpy())
            bAft = findavg(weekday_2pm.to_numpy())
            cAft = findmax(weekday_2pm.to_numpy())
            trafficMultiplierAft = pert(aAft,bAft,cAft)/100 + 1


            # if (len(totalRouteTime) != 31):
            newTimes = np.append((np.array(totalRouteTime)[0:30])*trafficMultiplierMorn, (np.array(totalRouteTime)[30:])*trafficMultiplierAft, axis = 0)
            # else:
            #     newTimes = totalRouteTime[0:30]*trafficMultiplierMorn
            #     newTimes.append(totalRouteTime[-1]*trafficMultiplierAft)
            #     newTimes = np.append

        # Calculate total cost
        WeekdayCost[i] = calcCost(newTimes)
        pass


    # Histogram
    plt.hist(WeekdayCost, histtype='stepfilled', alpha=0.2, label='Completion Times')
    plt.show()
    ##### SATURDAYS SIMULATION #######

    CountdownData = possibleDemands(data, 'Traditional', 'Saturday')

    # Repeat simulation for saturdays
    SaturdayCost = [0]*Simulations

    Demand = listStores()

    # Each Simulation
    for i in range(Simulations):
        # Calculate uncertain demands for each store
        for node in Demand.index:
            if (Demand.loc[node,'Class'] == "Traditional"):
                Demand.at[node] = BootstrapDemand(CountdownData)
            else:
                # add distribution centre and special stores with demand of 0
                Demand.at[node] = 0
        
        routes = satR
        for route in routes:
            # if demand on a route > truck capacity add a new route 
            if (sum([Demand.loc[node]['Class'] for node in route]) > 26):
                newRoutes = addRoute(route, Demand)
                routes.remove(route)
                for i in newRoutes:
                    routes.append(i)
                    
        # Calculate the total time taken by each route (in minutes)
        totalRouteTime = [0]*len(routes)
        for ind in range(len(routes)):
            totalRouteTime[ind] = (sum([Demand.loc[node]['Class'] for node in routes[ind]])*7.5 + calculateRouteTime(route)/60)

        # Traffic effect
        
        
        # Calculate total cost
        # SaturdayCost[i] = 

    # Histograms
    plt.hist(WeekdayCost, density=True, histtype='stepfilled', alpha=0.2)
    # plt.hist(ExpectedTimes, density=True, histtype='stepfilled', alpha=0.2)

    # Average cost time
    print("average cost: ", np.mean(WeekdayCost))

    # One sample t-test, with H0 = expected completion time.
    # print(stats.ttest_1samp(CompletionTimes, H0)) # change HO

    # Percentile interval
    WeekdayCost.sort()
    print(WeekdayCost[2], " to ", WeekdayCost[97])

    # # Error rate
    # error = sum(np.greater(CompletionTimes, ExpectedTimes))/len(CompletionTimes)
    # print("error = ", error)
