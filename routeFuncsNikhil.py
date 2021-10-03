import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count
import pickle
import datetime
from itertools import combinations

travelTimes = pd.read_csv('WoolworthsTravelDurations.csv', index_col=0)

def roundTripTime(source, destination):
    ''' Returns round trip time from source to destination.
        Inputs:
        ------
        travelTimes : pandas dataframe
                        dataframe containing travel durations.
        source      : string
                        string of source name.
        destination : string
                        string of destination name.
        
        Returns:
        --------
        tripTime : float
                    round trip time
    '''
    if (source == destination):
        ValueError('Source and Destination are the same.')

    tripTime = travelTimes.loc[source][destination] + travelTimes.loc[destination][source]
    return tripTime

def tripTime(source, destination):
    ''' Returns trip time from source to destination.
        Inputs:
        ------
        travelTimes : pandas dataframe
                        dataframe containing travel durations.
        source      : string
                        string of source name.
        destination : string
                        string of destination name.
        
        Returns:
        --------
        tripTime : float
                    trip time
    '''
    if (source == destination):
        ValueError('Source and Destination are the same.')

    tripTime = travelTimes.loc[source][destination]
    return tripTime

def calculateRouteTime(route):
    ''' 
        Calculates the route travel time for a given route.
        The route is assumed to be a round trip and thus after visiting the last location, a return to start location is assumed
        Parameters:
        -----------
        route : string list
                string list containing locations to visit in route.
                - The route is assumed to be a round trip and thus after visiting the last location, a return to start location is assumed
        travelTimes : pandas dataframe
                        given data on travel durations.
                        - use the default input.
        
        Returns:
        --------
        time : float
                Route time
    '''

    time = 0

    for i in range(len(route)):
        if (i == len(route) - 1):
            time += tripTime(route[i], route[0])

        else:
            time += tripTime(route[i], route[i+1])
        
        if(time > 14400): return np.inf # Exits loops if current route time over 4 hours and returns infinity if so.


    return time


def twoArcInterchange(storesArray):
    ''' Applies Two-Arc interchange approach (as described on pg 8 of coursebook) to find shortest path.
        Parameters:
        -----------
        storesArray : string Tuple
                        string list containing locations in route.
                        - distribution centre is assumed to be part of route so does not need to be in list.

        travelTimes : pandas dataframe
                        given data on travel durations.
                        - use the default input.
        
        Returns:
        --------
        minRoute       : string List
                        string list containing route.
                        - warehouse is always first as truck starts there.
                        - nodes are in ascending order of visit time.
    '''
    storesArray = list(storesArray)

    storesArray.append('Distribution Centre Auckland')

    minTime = calculateRouteTime(storesArray)
    minRoute = storesArray

    for swap1index in range(len(storesArray)):

        if (swap1index != len(storesArray) - 1):
            for swap2index in range(swap1index+1, len(storesArray)):
                currentRoute = storesArray # Initializing for currentRoute for each iteration.

                
                swap1 = storesArray[swap1index]
                swap2 = storesArray[swap2index]

                currentRoute[swap1index] = swap2
                currentRoute[swap2index] = swap1

                currentTime = calculateRouteTime(currentRoute)

                if (currentTime < minTime):
                    minTime = currentTime
                    minRoute = currentRoute

    if (minTime < np.inf):
        return minRoute
    else: # Returns none value if all routes are more than 4 hours long
        return None

def matrixForm(Routes, stores):
    ''' Creates a binary matrix of stores visited by each route
        Parameters:
        -----------
        Routes : list of string lists
                    string lists containing stores visited by a given route
        stores : string list
                    List of all stores in the network
                        - Should not include the distribution centre
        Returns:
        --------
        RoutesMatrix : pandas dataframe 
                        A binary matrix of whether each store was visited by a given route 
    '''
    RoutesDict={}

    for Routeindex in range(len(Routes)):
        Nodes = pd.Series([0]*len(stores), index=stores) # Initialise with zeros for each iteration
        for stop in Routes[Routeindex][1::]:             # Ignore the distribution centre
            Nodes[stop] = 1
        RoutesDict[Routeindex] = Nodes
    
    RoutesMatrix = pd.DataFrame(RoutesDict)
    return RoutesMatrix

if __name__ == "__main__":
    
    travelTimes = pd.read_csv('WoolworthsTravelDurations.csv', index_col=0)
    distances = pd.read_csv('WoolworthsDistances.csv', index_col=0)
    groupLocations = pd.read_csv('GroupedLocations.csv', index_col=0)

    groupLocations = groupLocations.loc[groupLocations['Type'] != 'Distribution Centre',]


    normalAvgDemand = 7.99
    specialAvgDemand = 4.41

    truckCapacity = 26

    possibleRoutesWkDay = []

    # Parallel processing tingz
    ncpus = cpu_count()
    p = Pool(ncpus)



    for i in range(6): # Loops over all groups to generate routes for weekdays.

        currentStores = groupLocations.loc[groupLocations['Group ' + str(i+1)] == 1,]
        currentTraditional = currentStores.loc[currentStores['Type'] == 'Countdown',]
        currentSpecial = currentStores.loc[(currentStores['Type'] == 'Countdown Metro') | \
                                        (currentStores['Type'] == 'FreshChoice') | \
                                        (currentStores['Type'] == 'SuperValue'),]

        # Generating all possible routes in current region.
        trad1Stores = list(combinations(currentTraditional['Store'],1))
        trad2Stores = list(combinations(currentTraditional['Store'],2))
        trad3Stores = list(combinations(currentTraditional['Store'],3))

        spec1Stores = list(combinations(currentSpecial['Store'], 1))
        spec2Stores = list(combinations(currentSpecial['Store'], 2))
        spec3Stores = list(combinations(currentSpecial['Store'], 3))
        spec4Stores = list(combinations(currentSpecial['Store'], 4))
        spec5Stores = list(combinations(currentSpecial['Store'], 5))

        # Routes with 2 normal and 2 special in current region:
        norm2spec2Stores = []

        for i1 in trad2Stores:
            for i2 in spec2Stores:
                norm2spec2Stores.append(i1 + i2)
        
        # Routes with 1 normal and 4 special in current region:
        norm1spec4Stores = []

        for i1 in trad1Stores:
            for i2 in spec4Stores:
                norm1spec4Stores.append(i1 + i2)
        
        # Forming shortest routes and adding them possible routes.
        possibleRoutesWkDay += p.map(twoArcInterchange, trad1Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, trad2Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, trad3Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, spec1Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, spec2Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, spec3Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, spec4Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, spec5Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, norm2spec2Stores)
        possibleRoutesWkDay += p.map(twoArcInterchange, norm1spec4Stores)


    # Filtering out routes with more than 4 hour run times.
    possibleRoutesWkDay = list(filter(None, possibleRoutesWkDay))

    # Saving week day routes.
    with open('savedWkDayRoutes.pkl', 'wb') as f:
        pickle.dump(possibleRoutesWkDay, f)
    

    possibleRoutesSat = []

    for i in range(6): # Loops over all groups to generate routes for saturday.

        currentStores = groupLocations.loc[groupLocations['Group ' + str(i+1)] == 1,]
        currentTraditional = currentStores.loc[currentStores['Type'] == 'Countdown',]
        

        stores1 = list(combinations(currentTraditional['Store'],1))
        stores2 = list(combinations(currentTraditional['Store'],2))
        stores3 = list(combinations(currentTraditional['Store'],3))
        stores4 = list(combinations(currentTraditional['Store'],4))
        stores5 = list(combinations(currentTraditional['Store'],5))
        stores6 = list(combinations(currentTraditional['Store'],6))

        possibleRoutesSat += p.map(twoArcInterchange, stores1)
        possibleRoutesSat += p.map(twoArcInterchange, stores2)
        possibleRoutesSat += p.map(twoArcInterchange, stores3)
        possibleRoutesSat += p.map(twoArcInterchange, stores4)
        possibleRoutesSat += p.map(twoArcInterchange, stores5)
        possibleRoutesSat += p.map(twoArcInterchange, stores6)

    # Filtering out routes with more than 4 hour run times.
    possibleRoutesSat = list(filter(None, possibleRoutesSat))

    with open('savedSatRoutes.pkl', 'wb') as f:
        pickle.dump(possibleRoutesSat, f)


    





    
    


    




