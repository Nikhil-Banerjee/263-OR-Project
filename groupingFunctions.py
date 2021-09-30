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






def assignNode(locationData, location, group1=0, group2=0, group3=0, group4=0, group5=0, group6=0):

    locationData.loc[locationData['Location'] == location, 'Group 1'] = group1
    locationData.loc[locationData['Location'] == location, 'Group 2'] = group2
    locationData.loc[locationData['Location'] == location, 'Group 3'] = group3
    locationData.loc[locationData['Location'] == location, 'Group 4'] = group4
    locationData.loc[locationData['Location'] == location, 'Group 5'] = group5
    locationData.loc[locationData['Location'] == location, 'Group 6'] = group6
    
    return locationData


if __name__ == "__main__":

    # Loading given data.
    distanceData = pd.read_csv('WoolworthsDistances.csv')
    locationData = pd.read_csv('WoolworthsLocations.csv')

    # Initializing grouping columns,
    locationData['Group 1'] = 0
    locationData['Group 2'] = 0
    locationData['Group 3'] = 0
    locationData['Group 4'] = 0
    locationData['Group 5'] = 0
    locationData['Group 6'] = 0

    # Example of assigning node.
    locationData = assignNode(locationData, 'Airport',group5=1, group6=1)

