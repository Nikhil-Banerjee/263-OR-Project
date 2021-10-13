from TrafficDistributionFunctions import get_mult
import pandas as pd
import numpy as np


def randomFunc():
    return 0

def calcCost(times):
    # Function assumes no wet lease trucks are used.

    truckCostNorm = 3.75 #per minute
    truckCostOT = 275/60  # per minute

    totalTrucks = len(times)

    cost = 0

    if (totalTrucks <= 60):
        
        for i in range(totalTrucks):

            if (times[i] <= 4*60):
                cost += truckCostNorm*times[i]
            else:
                cost+= truckCostNorm*2400 + truckCostOT*(times[i] - 2400)

    else:
        ValueError('Wet lease trucks formulation not yet made.')

    return cost

if __name__ == "__main__":

    congestion = pd.read_csv('AKL_congestion.csv', index_col=0)

    weekday_8am = (congestion[["8am","9am","10am","11am"]]).loc["Mon":"Fri"]
    weekday_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Mon":"Fri"]
    weekend_8am = (congestion[["8am","9am","10am","11am"]]).loc["Sat":"Sun"]
    weekend_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Sat":"Sun"]

    wkDayMornMean = np.mean(weekday_8am.stack())


    wkDayAftMean = np.mean(weekday_2pm.stack())



    # Provided Weekday routes.
    currentRoutes = []
    currentTimes = []

    newTimes = []

    wkDaySims = len(currentRoutes)

    completionTimes = [0]*wkDaySims

    for i in range(wkDaySims):
        if (i <= 30): # Faster to deliver in morning on average so allocates first 30 routes to be in the morning.
            multiplier = get_mult(weekday_8am)/100 + 1
        else:
            multiplier = get_mult(weekday_2pm)/100 + 1
        
        newTimes[i] = multiplier * currentTimes[i]
    

    








































































