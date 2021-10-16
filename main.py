import numpy as np
import pandas as pd
import math
import pickle
from pulp import *
from routeFuncsNikhil import *



def main():
    '''
    Contains the LP formulation for both weekday form
    Prints the optimal solutions to the LP
    Saves the optimal routes for use in simulation
    '''
    truckCost = 3.75 # per minute (225/60 = 3.75)
    truckFleet = 30
    truckCapacity = 26

    unloadTime = 7.5        # in minutes
    maxRouteTime = 4 * 60   # in minutes

    # Read in data from supplied csv's
    travelTimes = pd.read_csv('WoolworthsTravelDurations.csv', index_col=0)
    demands = pd.read_csv('WoolworthsDemands.csv', index_col=0)
    locations = pd.read_csv('WoolworthsLocations.csv')

    # Data formatting
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
        probWkDay += lpSum([wkDayDemand[store]*wkDay_route_vars[route]*wkDayRoutes[route][store] for store in stores])   <= truckCapacity
        #  4 hour time limit is not surpassed for any route
        probWkDay += lpSum(calculateRouteTime(wkDayR[route])/60+lpSum([unloadTime*wkDayDemand[store]*wkDay_route_vars[route]*wkDayRoutes[route][store] for store in stores])) <= maxRouteTime
    
    # The problem data is written to an .lp file
    probWkDay.writeLP("WeekdayProblem.lp")
    # The problem is solved using PuLP's choice of Solver
    probWkDay.solve()

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[probWkDay.status])
    # Each of the optimal routes used is saved
    UsedWkDayRoutes=[]
    for v in probWkDay.variables():
        if v.varValue == 1.0:
	        UsedWkDayRoutes.append(wkDayR[int(v.name[11:])])
    with open('UsedWkDayRoutes.pkl', 'wb') as f:
        pickle.dump(UsedWkDayRoutes, f)
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
    # Each of the optimal routes used is saved
    UsedSatRoutes=[]
    for v in probSat.variables():
        if v.varValue == 1.0:
	        UsedSatRoutes.append(satR[int(v.name[11:])])
    with open('UsedSatRoutes.pkl', 'wb') as f:
        pickle.dump(UsedSatRoutes, f)
    # The optimised objective function value is printed to the screen
    print("Delivery Costs (Sat) = ", value(probSat.objective))


def averageDemand(demandData, day):
    '''
    Calculates and returns average demand based on weekday or saturday
    Inputs:
    	demandData : pandas dataframe
			- Table of daily demands at a given store
	day : string 
			- either "Weekday" or "Saturday" to return the corresponding set
    Returns:
        averages : pandas Series
			- The average demand for each store for the specified day(s) 
		
    '''
    size = demandData.shape
    averages = pd.Series([0]*size[0],index=demandData.index)

    for i in range(size[0]):                            # For every store
        divisor=0
        for j in range(size[1]):                        # For every day
	    # Separating based on weekday/saturday
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

if __name__ == "__main__":
	main()
