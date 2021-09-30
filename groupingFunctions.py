import numpy as np
import pandas as pd
import math
from pulp import *
from routeFunctions import *

def CreateGroups(distanceData,locationData):
    
    # initialising number of nearest nodes
    k = 15

    # Create a list of starting nodes to create groups around based of geographical intuition
    startingNodes = ['Countdown Lynfield','Countdown Manukau Mall','Countdown Henderson','Countdown Highland Park','Countdown Mt Eden','Countdown Milford']

    # loop through starting nodes
    for node in startingNodes:
        # extracting the row of distances from the starting node
        distances = distanceData.loc[node,:]
        # sorting the distances
        distances = distances.sort()
        # selection the k smallest distances
        closestNodeDistances = distances[:k]
        # extracting names of closest nodes
        for i in closestNodeDistances:
            
            #.index(i)





    pass



def main():
    distanceData = pd.read_csv("WoolworthsTravelDurations.csv",sep=",",header=0,index_col=0)
    locationsData = pd.read_csv("WoolworthsLocations.csv",sep=",",header=0,index_col=0)