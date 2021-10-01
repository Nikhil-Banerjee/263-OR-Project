import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count
import pickle
import datetime

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


def cheapestInsertion(storesArray):
    ''' Applies Two-Arc interchange approach (as described on pg 8 of coursebook) to find shortest path.
        Parameters:
        -----------
        storesArray : string List
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

    storesArray.append('Distribution Centre Auckland')

    minTime = calculateRouteTime(storesArray)
    minRoute = storesArray

    for swap1index in range(len(storesArray)):
        currentRoute = storesArray # Initializing for currentRoute for each iteration.

        if (swap1index != len(storesArray) - 1):
            for swap2index in range(swap1index+1, len(storesArray)):
                
                swap1 = storesArray[swap1index]
                swap2 = storesArray[swap2index]

                currentRoute[swap1index] = swap2
                currentRoute[swap2index] = swap1

                currentTime = calculateRouteTime(currentRoute)

                if (currentTime < minTime):
                    minTime = currentTime
                    minRoute = currentRoute
    

    return minRoute

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

    print('Started route generation at {}'.format(datetime.datetime.now()))
    
    travelTimes = pd.read_csv('WoolworthsTravelDurations.csv', index_col=0)
    distances = pd.read_csv('WoolworthsDistances.csv', index_col=0)
    groupLocations = pd.read_csv('GroupedLocations.csv', index_col=0)


    normalAvgDemand = 7.99
    specialAvgDemand = 4.41

    truckCapacity = 26

    possibleRoutes = []

    # Parallel processing tingz
    ncpus = cpu_count()
    p = Pool(ncpus)



    for i in range(6): # Loops over all groups

        currentStores = groupLocations.loc[groupLocations['Group ' + str(i+1)] == 1,]
        currentTraditional = currentStores.loc[currentStores['Type'] == 'Countdown',]
        currentSpecial = currentStores.loc[(currentStores['Type'] == 'Countdown Metro') | \
                                        (currentStores['Type'] == 'FreshChoice') | \
                                        (currentStores['Type'] == 'SuperValue'),]

        # Generating all possible routes in current region.
        currentPossibleRoutes = []

        trad3Stores = []

        # All routes with 3 traditional stores
        for index1, row1 in currentTraditional.iterrows():
            for index2, row2 in currentTraditional[currentTraditional['Store'] != row1['Store']].iterrows():
                for index3, row3 in currentTraditional[(currentTraditional['Store'] != row1['Store']) & \
                                                    (currentTraditional['Store'] != row2['Store'])].iterrows():

                    currentStores = [row1['Store'], row2['Store'], row3['Store']]
                    # currentPossibleRoutes.append(cheapestInsertion(currentStores))

                    trad3Stores.append(currentStores)


        trad2spec2Stores = []
        
        # All routes with 2 traditional and 2 special in current region.
        for index1, row1 in currentTraditional.iterrows():
            for index2, row2 in currentTraditional[currentTraditional['Store'] != row1['Store']].iterrows():
                for index3, row3 in currentSpecial.iterrows():
                    for index4, row4 in currentSpecial[currentSpecial['Store'] != row3['Store']].iterrows():

                        currentStores = [row1['Store'], row2['Store'], row3['Store'], row4['Store']]
                        # currentPossibleRoutes.append(cheapestInsertion(currentStores))
                        trad2spec2Stores.append(currentStores)
        

        trad1spec4Stores = []

        # All routes with 1 traditional and 4 special in current region.
        for index1, row1 in currentSpecial.iterrows():
            for index2, row2 in currentSpecial[currentSpecial['Store'] != row1['Store']].iterrows():
                for index3, row3 in currentSpecial[(currentSpecial['Store'] != row1['Store']) & \
                                                (currentSpecial['Store'] != row2['Store'])].iterrows():
                    for index4, row4 in currentSpecial[(currentSpecial['Store'] != row1['Store']) & \
                                                    (currentSpecial['Store'] != row2['Store']) & \
                                                    (currentSpecial['Store'] != row3['Store'])].iterrows():
                        for index5, row5 in currentTraditional.iterrows():
                            
                            currentStores = [row1['Store'], row2['Store'], row3['Store'], row4['Store'], row5['Store']]
                            # currentPossibleRoutes.append(cheapestInsertion(currentStores))
                            trad1spec4Stores.append(currentStores)
        
        trad3StoresResults = p.map(cheapestInsertion, trad3Stores)
        print('Finished group {}, route search for 3 traditional stores at {}'.format(i, datetime.datetime.now()))

        trad2spec2Results = p.map(cheapestInsertion, trad2spec2Stores)
        print('Finished group {}, route search for 2 traditional and 2 special stores at {}'.format(i, datetime.datetime.now()))

        trad1spec4Results = p.map(cheapestInsertion, trad1spec4Stores)
        print('Finished group {}, route search for 1 traditional and 4 special stores at {}'.format(i, datetime.datetime.now()))
        

        possibleRoutes += trad3StoresResults + trad2spec2Results + trad1spec4Results


    with open('savedRoutes.pkl', 'wb') as f:
        pickle.dump(possibleRoutes, f)
        




    
    


    




