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
from os import sep


def groupDemands():
    '''
    
    '''
    data = pd.read_csv('Store Closing files' + sep + 'WoolworthsDemandsV2.csv')
    
    # Tidies the data by having 3 columns in dataframe: Store, Date and Demand.
    data = data.melt(id_vars = 'Store', var_name = 'Date', value_name = 'Demand')
    
    # Creates new column 'Day Type' which classifies days of the week into: weekday, saturday and sunday.
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
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
    stores = pd.read_csv('Store Closing files' + sep + 'WoolworthsLocationsV2.csv')
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
    while sum([Demands.loc[node,'demand'] for node in Route]) > 26:
        newRoutes.append('')
        for index in range(1,len(Route)):
            if (calculateRouteTime(Route[0:index] + Route[index+1:]) + roundTripTime('Distribution Centre Auckland', Route[index])) < time:
                time = calculateRouteTime(Route[0:index] + Route[index+1:]) + roundTripTime('Distribution Centre Auckland', Route[index])
                newRoutes[0] = Route[0:index] + Route[index+1:]
                newRoutes[-1] = ['Distribution Centre Auckland', Route[index]]
        Route = newRoutes[0]
    
    return newRoutes

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
    Simulations = 1000
        
    #Read in route information
    with open('Store Closing files' + sep + 'UsedWkDayRoutes.pkl', 'rb') as f:
        wkDayR = pickle.load(f)
    with open('Store Closing files' + sep + 'UsedSatRoutes.pkl', 'rb') as f:
        satR = pickle.load(f)

    
    congestion = pd.read_csv('AKL_congestion.csv', index_col=0)

    ##### WEEKDAYS SIMULATION ######
    weekday_8am = (congestion[["8am","9am","10am","11am"]]).loc["Mon":"Fri"]
    weekday_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Mon":"Fri"]

    # Extracting weekday data
    CountdownData = possibleDemands(data, 'Traditional', 'Week Day')
    SpecialData = possibleDemands(data, 'Special', 'Week Day')

    WeekdayCost = [0]*Simulations

    initialDemand = listStores()

    # Each Simulation
    for i in range(Simulations):

        Demand = initialDemand
        Demand['demand'] = 0
        # Calculate uncertain demands for each store
        for node in Demand.index:
            if (Demand.loc[node,'Class'] == "Traditional"):
                Demand.loc[node,'demand'] = BootstrapDemand(CountdownData)
            elif (Demand.loc[node,'Class'] == "Distribution Centre"):
                # add distribution centre with demand of 0
                Demand.loc[node,'demand'] = 0
            else:
                Demand.loc[node,'demand'] = BootstrapDemand(SpecialData)
        
        routes = wkDayR
        for route in routes:
            # if demand on a route > truck capacity add a new route 
            if (sum([Demand.loc[node,'demand'] for node in route]) > 26):
                newRoutes = addRoute(route, Demand)
                routes.remove(route)
                for j in newRoutes:
                    routes.append(j)
                    
        # Calculate the total time taken by each route (in minutes)
        totalRouteTime = np.zeros(len(routes))
        for ind in range(len(routes)):
            totalRouteTime[ind] = (sum([Demand.loc[node,'demand'] for node in routes[ind]])*7.5 + calculateRouteTime(routes[ind])/60)
        
        # Traffic effect
        if (len(totalRouteTime) <= 30):
            meanMorn = findavg(weekday_8am.to_numpy())

            trafficMultiplierMorn = np.random.exponential(meanMorn, 1)/100 + 1

            newTimes = totalRouteTime*trafficMultiplierMorn

        else:
            meanMorn = findavg(weekday_8am.to_numpy())

            trafficMultiplierMorn = np.random.exponential(meanMorn, 1)/100 + 1


            meanAft = findavg(weekday_2pm.to_numpy())
            trafficMultiplierAft = np.random.exponential(meanAft, 1)/100 + 1


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
    hist1 = plt.figure(1)
    plt.hist(WeekdayCost, histtype='stepfilled', alpha=0.2, label='Completion Times for Week day')
    plt.title("Weekday Cost of Operations Distribution")
    plt.xlabel('Cost per day ($)')
    plt.ylabel('Frequency')

    with open('savedWkDayRemSim.pkl','wb') as f:
        pickle.dump(WeekdayCost, f)

    ##### SATURDAYS SIMULATION #######
    weekend_8am = (congestion[["8am","9am","10am","11am"]]).loc["Sat":"Sun"]
    weekend_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Sat":"Sun"]

    CountdownData = possibleDemands(data, 'Traditional', 'Saturday')

    # Repeat simulation for saturdays
    SaturdayCost = [0]*Simulations

    initialDemand = listStores()

    satCost = [0]*Simulations

    # Each Simulation
    for i in range(Simulations):

        Demand = initialDemand
        Demand['demand'] = 0
        # Calculate uncertain demands for each store
        for node in Demand.index:
            if (Demand.loc[node,'Class'] == "Traditional"):
                Demand.loc[node,'demand'] = BootstrapDemand(CountdownData)
            else:
                # add distribution centre and special stores with demand of 0
                Demand.loc[node,'demand'] = 0

        routes = satR
        for route in routes:
            # if demand on a route > truck capacity add a new route 
            if (sum([Demand.loc[node,'demand'] for node in route]) > 26):
                newRoutes = addRoute(route, Demand)
                routes.remove(route)
                for j in newRoutes:
                    routes.append(j)
                    
         # Calculate the total time taken by each route (in minutes)
        totalRouteTime = np.zeros(len(routes))
        for ind in range(len(routes)):
            totalRouteTime[ind] = (sum([Demand.loc[node,'demand'] for node in routes[ind]])*7.5 + calculateRouteTime(routes[ind])/60)
        

        # Traffic effect
        if (len(totalRouteTime) <= 30):
            meanMorn = findavg(weekend_8am.to_numpy())
            trafficMultiplierMorn = np.random.exponential(meanMorn, 1)/100 + 1

            newTimes = totalRouteTime*trafficMultiplierMorn
        
        else:
            meanMorn = findavg(weekend_8am.to_numpy())
            trafficMultiplierMorn = np.random.exponential(meanMorn, 1)/100 + 1


            meanAft = findavg(weekend_2pm.to_numpy())
            trafficMultiplierAft = np.random.exponential(meanAft, 1)/100 + 1

            newTimes = np.append((np.array(totalRouteTime)[0:30])*trafficMultiplierMorn, (np.array(totalRouteTime)[30:])*trafficMultiplierAft, axis = 0)

        # Calculate total cost
        satCost[i] = calcCost(newTimes)

    # Histogram
    hist2 = plt.figure(2)
    plt.hist(satCost, histtype='stepfilled', alpha=0.2, label='Completion Times for Saturday')
    plt.title("Saturday Cost of Operations Distribution")
    plt.xlabel('Cost per day ($)')
    plt.ylabel('Frequency')
    # plt.hist(ExpectedTimes, density=True, histtype='stepfilled', alpha=0.2)

    with open('savedSatDayRemSim.pkl','wb') as f:
        pickle.dump(satCost, f)

    # Average cost time
    print("Weekday average cost: ", np.mean(WeekdayCost))
    print("Saturday average cost: ", np.mean(satCost))

    # One sample t-test, with H0 = expected completion time.
    # print(stats.ttest_1samp(CompletionTimes, H0)) # change HO

    # Percentile interval
    WeekdayCost.sort()
    print("Weekday interval", WeekdayCost[25], " to ", WeekdayCost[975])
    satCost.sort()
    print("Saturday interval", satCost[25], " to ", satCost[975])

    # # Error rate
    # error = sum(np.greater(CompletionTimes, ExpectedTimes))/len(CompletionTimes)
    # print("error = ", error)
    plt.show()
    plt.savefig('Hist.png')

