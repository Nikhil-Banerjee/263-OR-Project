import numpy as np
import pandas as pd
import math
import pickle
from pulp import *

travelTimes = pd.read_csv('WoolworthsTravelDurations.csv', index_col=0)

def main():
    demands = loadDemands()

    truckCost = 3.75 # per minute (225/60 = 3.75)
    truckFleet = 30
    truckCapacity = 26

    unloadTime = 7.5        # in minutes
    maxRouteTime = 4 * 60   # in minutes

    demands = pd.read_csv('WoolworthsDemands.csv', index_col=0)
    locations = pd.read_csv('WoolworthsLocations.csv')
    stores = demands.index

    satstores = locations[locations['Type'] == 'Countdown']['Store']
    wkDayDemand = averageDemand(demands,"Weekday")
    satDemand = averageDemand(demands,"Saturday")

    #Read in route information
    with open('savedWkDayRoutes.pkl', 'rb') as f:
        wkDayR = pickle.load(f)
    with open('savedWkDayTimes.pkl', 'rb') as f:
        wkDayTimes = pickle.load(f)
    with open('savedSatRoutes.pkl', 'rb') as f:
        satR = pickle.load(f)
    with open('savedSatTimes.pkl', 'rb') as f:
        satTimes = pickle.load(f)
    wkDayR=hardcode()
    wkDayTimes=[0]*30
    wkDayRoutes=matrixForm(wkDayR, stores)
    satRoutes=matrixForm(satR, stores)
    
    

    # Actual LP formulation
    probWkDay = LpProblem("Week Day LP", LpMinimize)

    # Assigning Decision Variables
    index=pd.RangeIndex(0,len(wkDayTimes))
    wkDay_route_vars = LpVariable.dicts("RoutesUsed",index,cat=LpBinary)
    wkDayExtraTrucks = LpVariable("extraTrucks", lowBound = 0, cat = 'Integer')
    
    # Objective function
    probWkDay += lpSum([wkDay_route_vars[i] * truckCost * (calculateRouteTime(wkDayR[i])/60  + lpSum([wkDayRoutes[i][store]*wkDayDemand[store] * unloadTime for store in stores])) + 2000 * wkDayExtraTrucks for i in range(len(wkDayTimes))])
    #probWkDay += lpSum([wkDay_route_vars[i] * truckCost * (wkDayTimes[i]/60) + 2000 * wkDayExtraTrucks for i in range(len(wkDayTimes))])
    # Extra constraints
    probWkDay += lpSum(lpSum(wkDay_route_vars) - wkDayExtraTrucks) <= 2*truckFleet  # Constraint for # of trucks
    for store in stores:
        # That every store should receive a delivery (Assuming a delivery delivers all pallets demanded)
        probWkDay += lpSum([wkDay_route_vars[i] * wkDayRoutes[i][store] for i in wkDayRoutes]) >= 1
    for route in range(wkDayRoutes.shape[1]):
        # Truck capacity is not surpassed for any route
        #probWkDay += lpSum([wkDayDemand[store]*wkDay_route_vars[route]*wkDayRoutes[route][store] for store in stores])   <= truckCapacity
        #  4 hour time limit is not surpassed for any route
        probWkDay += lpSum(calculateRouteTime(wkDayR[route])/60+lpSum([unloadTime*wkDayDemand[store]*wkDay_route_vars[route]*wkDayRoutes[route][store] for store in stores])) <= maxRouteTime
    
    # The problem data is written to an .lp file
    probWkDay.writeLP("WeekdayProblem.lp")
    # The problem is solved using PuLP's choice of Solver
    probWkDay.solve()

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[probWkDay.status])
    # Each of the variables is printed with it's resolved optimum value
    for v in probWkDay.variables():
        if v.varValue == 1.0:
	        print(wkDayR[int(v.name[11:])])
    # The optimised objective function value is printed to the screen
    print("Delivery Costs = ", value(probWkDay.objective))



    # Same formulation but for Saturday
    probSat = LpProblem("Saturday LP", LpMinimize)

    # Assigning Decision Variables
    index=pd.RangeIndex(0,len(satTimes))
    sat_route_vars = LpVariable.dicts("RoutesUsed",index,cat='Binary')
    satExtraTrucks = LpVariable("extraTrucks", lowBound = 0, cat = 'Integer')
    
    # Objective function
    probSat += lpSum([sat_route_vars[i] * truckCost * (calculateRouteTime(satR[i])/60 + lpSum([satRoutes[i][store]*satDemand[store] * unloadTime for store in satstores])) + 2000 * satExtraTrucks for i in range(len(satTimes))])

    # Extra constraints
    probSat += lpSum(lpSum(sat_route_vars) - satExtraTrucks) <= 2*truckFleet # Constraint for # of trucks
    for store in satstores:
        # That every store should receive a delivery (Assuming a delivery delivers all pallets demanded)
        probSat += lpSum([sat_route_vars[i] * satRoutes[i][store] for i in satRoutes]) >= 1
    for route in range(satRoutes.shape[1]):
        # Truck capacity is not surpassed for any route
        probSat += lpSum([satDemand[store]*sat_route_vars[route]*satRoutes[route][store] for store in stores])   <= truckCapacity
        # 4 hour time limit is not surpassed for any route
        #probSat += lpSum(calculateRouteTime(satR[route])/60+lpSum([unloadTime*satDemand[store]*sat_route_vars[route]*satRoutes[route][store] for store in stores])) <= maxRouteTime
    
    # The problem data is written to an .lp file
    probSat.writeLP("SaturdayProblem.lp")
    # The problem is solved using PuLP's choice of Solver
    probSat.solve()

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[probSat.status])
    # Each of the variables is printed with it's resolved optimum value
    for v in probSat.variables():
        if v.varValue == 1.0:
	        print(satR[int(v.name[11:])])
    # The optimised objective function value is printed to the screen
    print("Delivery Costs (Sat) = ", value(probSat.objective))


def averageDemand(demandData, day):
    size = demandData.shape
    averages = pd.Series([0]*size[0],index=demandData.index)
    for i in range(size[0]):                            # For every store
        divisor=0
        for j in range(size[1]):                        # For every day
            if day == 'Saturday':
                if j%7 == 5:
                    averages[i]+=demandData.iat[i,j]
                    divisor+=1
            if day == 'Weekday':
                if j%7 != 5 and j%7 != 6:
                    averages[i]+=demandData.iat[i,j]
                    divisor+=1
        averages[i] = math.ceil(averages[i]/divisor)
    return averages


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


def loadDemands():
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

    # Calculating requried means.
    data = (data.groupby(['Day Type','Store Type'])['Demand']
                .mean())

    return data


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

def hardcode():
    routes = []
    routes.append(['Distribution Centre Auckland', 'Countdown St Lukes', 'Countdown Pt Chevalier', 'Countdown Grey Lynn Central'])
    routes.append(['Distribution Centre Auckland', 'Countdown Mt Eden', 'Countdown Victoria Street West', 'Countdown Metro Halsey Street', 'Countdown Metro Albert Street'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Mangere Bridge', 'Countdown Mt Roskill'])
    routes.append(['Distribution Centre Auckland', 'Countdown Onehunga', 'Countdown Three Kings'])
    routes.append(['Distribution Centre Auckland', 'Countdown Lynmall', 'SuperValue Avondale'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Glen Eden', 'Countdown Kelston'])
    routes.append(['Distribution Centre Auckland', 'Countdown Lynfield', 'Countdown Blockhouse Bay', 'SuperValue Titirangi'])
    routes.append(['Distribution Centre Auckland', 'Countdown Birkenhead', 'Countdown Glenfield'])
    routes.append(['Distribution Centre Auckland', 'Countdown Milford', 'Countdown Browns Bay'])
    routes.append(['Distribution Centre Auckland', 'Countdown Sunnynook', 'Countdown Mairangi Bay'])
    routes.append(['Distribution Centre Auckland', 'SuperValue Papakura', 'Countdown Papakura', 'Countdown Roselands'])
    routes.append(['Distribution Centre Auckland', 'Countdown Ponsonby', 'Countdown Grey Lynn'])
    routes.append(['Distribution Centre Auckland', 'Countdown Takanini', 'Countdown Manurewa', 'Countdown Manukau Mall'])
    routes.append(['Distribution Centre Auckland', 'Countdown Airport', 'Countdown Mangere Mall', 'Countdown Mangere East'])
    routes.append(['Distribution Centre Auckland', 'Countdown Manukau', 'SuperValue Flatbush', 'Countdown Papatoetoe'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Ranui', 'Countdown Lincoln Road'])
    routes.append(['Distribution Centre Auckland', 'Countdown Te Atatu', 'Countdown Hobsonville'])
    routes.append(['Distribution Centre Auckland', 'Countdown Westgate', 'Countdown Northwest'])
    routes.append(['Distribution Centre Auckland', 'SuperValue Palomino', 'Countdown Henderson', 'Countdown Te Atatu South'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Otahuhu', 'Countdown Mt Wellington', 'Countdown Sylvia Park'])
    routes.append(['Distribution Centre Auckland', 'Countdown Botany Downs', 'Countdown Meadowlands', 'Countdown Howick'])
    routes.append(['Distribution Centre Auckland', 'Countdown Greenlane', 'Countdown Newmarket', 'Countdown Auckland City'])
    routes.append(['Distribution Centre Auckland', 'Countdown Pakuranga', 'Countdown Highland Park', 'Countdown Aviemore Drive'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Half Moon Bay', 'Countdown St Johns', 'Countdown Meadowbank'])

    routes.append(['Distribution Centre Auckland', 'Countdown Takapuna', 'Countdown Northcote', 'Countdown Hauraki Corner'])
    routes.append(['Distribution Centre Auckland', 'Countdown Takapuna', 'Countdown Hauraki Corner', 'Countdown Northcote'])
    routes.append(['Distribution Centre Auckland', 'Countdown Hauraki Corner', 'Countdown Northcote', 'Countdown Takapuna'])
    routes.append(['Distribution Centre Auckland', 'Countdown Hauraki Corner', 'Countdown Takapuna', 'Countdown Northcote'])
    routes.append(['Distribution Centre Auckland', 'Countdown Northcote', 'Countdown Takapuna', 'Countdown Hauraki Corner'])
    routes.append(['Distribution Centre Auckland', 'Countdown Northcote', 'Countdown Hauraki Corner', 'Countdown Takapuna'])

    return routes

if __name__ == "__main__":
	main()
