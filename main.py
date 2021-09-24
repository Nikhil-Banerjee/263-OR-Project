import numpy as np
import pandas as pd
import math
from pulp import *
from routeFunctions import *

def main():
    # Data reading
    dataDemands = np.genfromtxt("WoolworthsDemands.csv",dtype=None,delimiter=",",skip_header=1)
    distanceData = pd.read_csv("WoolworthsTravelDurations.csv",sep=",",header=0,index_col=0)

    # Problem/data definitions
    Demand=averageDemand(dataDemands)
    Stores=[]
    for row in dataDemands:
        Stores.append(str(row[0])[3:-2])
    '''
    RouteNames, RouteTimes, Routes = generateRoutes(Stores, distanceData)
    Routes=[#Placeholder to indicate formatting, intention being to read in generated routes from another python file
            [1,0,2], #Store 1 ...
            [2,3,0], #Store n
            ]
    RouteNames=["R1","R2", "R3"]
    Routes = makeDict([Stores,RouteNames],Routes,0)
    vars = LpVariable.dicts("Rout",RouteNames,0,None,LpInteger) 
    prob = LpProblem("Vehicle Routing Problem",LpMinimize)
    '''

    # Problem Constraints (starting with objective function)
    # Format: prob += condition >= RHS



    # Writing/Solving
    '''
    prob.writeLP("VehicleRoutingProblem.lp")
    prob.solve()
    '''

def averageDemand(dataTable):
    # At present computes average for each day for each store separately and returns a list of those values in a 7 day cycle
    # Is dependent on what the first day in the dataset is, could potentially calibrate it to the 0 deliveries on Sunday
    averages=np.array([[0.]*7]*len(dataTable))
    length=len(dataTable[0])-1
    for i in range(len(dataTable)):
        row=[]
        for j in range(1,len(dataTable[0])):
            row.append(float(dataTable[i][j]))
        for j in range(len(row)):
            averages[i][j%7]+=row[j]
        for j in range(7):
            divisor=math.floor(length/7)
            if ((length)%7)-j >0:
                divisor+=1
            averages[i][j]=math.ceil(averages[i][j]/divisor)
    return averages

if __name__ == "__main__":
	main()
