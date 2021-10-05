from re import M
import numpy as np
import pandas as pd
from pulp import *
import pickle
from itertools import repeat
from multiprocessing import Pool, cpu_count



def loadDemandAverages():
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

def locationInRoute(Route, location):
    ''' Returns true if location exists in route, false otherwise.
    '''

    for currentLoc in Route:
        if (location == currentLoc):
            return True
    
    return False


if __name__ == "__main__":
    
    demands = loadDemandAverages()

    truckCost = 3.75 # per minute (225/60 = 3.75)
    truckFleet = 30
    truckCapacity = 26

    extraTruckCost = 2000 # For 4 hour slots

    unloadTime = 7.5 # in minutes
    maxRouteTime = 4*60 # in minutes

    #Read in route information
    with open('savedWkDayRoutes.pkl', 'rb') as f:
        wkDayRoutes = pickle.load(f)
    with open('savedWkDayTimes.pkl', 'rb') as f:
        wkDayTimes = np.array(pickle.load(f))/60 # Loading times in minutes.
    with open('savedSatRoutes.pkl', 'rb') as f:
        satRoutes = pickle.load(f)
    with open('savedSatTimes.pkl', 'rb') as f:
        satTimes = np.array(pickle.load(f))/60 # Loading times in minutes.
    
    morningWkDay = pd.DataFrame({'Route' : wkDayRoutes,
                                    'Time' : wkDayTimes})
    
    # Parallel processing tingz
    ncpus = cpu_count()
    p = Pool(ncpus)

    # Forming columns which indicate if a particular route is visited or not.
    locations = pd.read_csv('WoolworthsLocations.csv')
    locations = locations.loc[locations['Store'] != 'Distribution Centre Auckland', 'Store']

    for currentLoc in locations:
        boolList = p.starmap(locationInRoute, zip(morningWkDay['Route'], repeat(currentLoc)))

        morningWkDay[currentLoc] = boolList

    
    afternoonWkDay = morningWkDay
    morningExtraWkDay = morningWkDay
    afternoonExtraWkDay = morningWkDay

    # Formulating the LP problem.
    probWkDay = LpProblem('Week Day LP', LpMinimize)

    # Forming variables for week day LP
    # Creates list of binary variables representing if a particular route is used or not in that specific morning/afternoon/extra run.
    morningVars = []
    afternoonVars = []
    morningExtraVars = []
    afternoonExtraVars = []

    for i in range(len(wkDayTimes)):
        morningVars.append(LpVariable('Morning route ' + str(i), cat = 'Binary'))

        afternoonVars.append(LpVariable('Afternoon route ' + str(i), cat = 'Binary'))
        
        morningExtraVars.append(LpVariable('Extra morning route ' + str(i), cat = 'Binary'))
        
        afternoonExtraVars.append(LpVariable('Extra afternoon route ' + str(i), cat = 'Binary'))
 
    # Adding vars to pandas df
    morningWkDay['Used'] = morningVars
    afternoonWkDay['Used'] = afternoonVars
    morningExtraWkDay['Used'] = morningExtraVars
    afternoonExtraWkDay['Used'] = morningExtraVars


    # Objective function (note: does not take into account cost if trip time over 4 hours)
    probWkDay += lpSum(truckCost * morningWkDay[morningWkDay['Used'] == 1]['Time']) \
                + lpSum(truckCost * afternoonWkDay[afternoonWkDay['Used'] == 1]['Time']) \
                + lpSum(extraTruckCost * morningExtraWkDay['Used']) \
                + lpSum(extraTruckCost * afternoonExtraWkDay['Used']), 'Total Costs'
    
    # Fleet constraints
    probWkDay += lpSum(morningExtraWkDay['Used'] <= 30), 'Morning fleet constraint'
    probWkDay += lpSum(afternoonExtraWkDay['Used'] <= 30), 'Afternoon fleet constraint'

    # Time constraints for each route (unncessary as we don't supply routes over 4 hours but just to be sure)
    # for index, row in morningWkDay.iterrows():
    #     probWkDay += row['Time']*row['Used'] <= maxRouteTime, 'Route ' + str(index) + ' morning time constraint'
    
    # for index, row in afternoonWkDay.iterrows():
    #     probWkDay += row['Time']*row['Used'] <= maxRouteTime, 'Route ' + str(index) + ' afternoon time constraint'

    # for index, row in morningExtraWkDay.iterrows():
    #     probWkDay += row['Time']*row['Used'] <= maxRouteTime, 'Route ' + str(index) + ' morning extra time constraint'

    # for index, row in afternoonExtraWkDay.iterrows():
    #     probWkDay += row['Time']*row['Used'] <= maxRouteTime, 'Route ' + str(index) + ' afternoon extra time constraint'
    




    # Each store gets a delivery (assuming each delivery delivers all pallets)
    # for currentLoc in locations:
    #     probWkDay += morningWkDay[morningWkDay['Used'] == 1][currentLoc].sum() \
    #                 + afternoonWkDay[afternoonWkDay['Used'] == 1][currentLoc].sum() \
    #                 + morningExtraWkDay[morningExtraWkDay['Used'] == 1][currentLoc].sum() \
    #                 + afternoonExtraWkDay[afternoonExtraWkDay['Used'] == 1][currentLoc].sum() >= 1, currentLoc + ' delivery constraint'

    for currentLoc in locations:
        probWkDay += (morningWkDay[currentLoc]*morningWkDay['Used']).sum() \
                    + (afternoonWkDay[currentLoc]*afternoonWkDay['Used']).sum() \
                    + (morningExtraWkDay[currentLoc]*morningExtraWkDay['Used']).sum() \
                    + (afternoonExtraWkDay[currentLoc]*afternoonExtraWkDay['Used']).sum() >= 1, currentLoc + ' delivery constraint'



    # The problem data is written to an .lp file
    probWkDay.writeLP("WeekdayProblem.lp")
    # The problem is solved using PuLP's choice of Solver
    probWkDay.solve()

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[probWkDay.status])

    # Each of the variables is printed with it's resolved optimum value
    for v in probWkDay.variables():
	    print(v.name, "=", v.varValue)
    # The optimised objective function value is printed to the screen
    print("Delivery Costs = ", value(probWkDay.objective))



    
    pass