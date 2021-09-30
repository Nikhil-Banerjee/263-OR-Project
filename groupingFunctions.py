import numpy as np
import pandas as pd
import math
from pulp import *
from routeFunctions import *

def CreateGroups(distanceData,locationData,startingNodes):
    
    # initialising number of nearest nodes
    k = 15

    # loop through starting nodes
    for node in startingNodes:
        group = [0,0,0,0,0,0]
        group[startingNodes.index(node)] = 1
        # extracting the row of distances from the starting node
        distances = distanceData.loc[node,:]
        # sorting the distances
        distances = distances.sort_values()
        # selection the k smallest distances
        closestNodeDistances = distances[:k]
        # extracting names of closest nodes
        for i in closestNodeDistances.index:
            assignNode(locationData, i, group=group)
pass


def assignNode(locationData, location, group = [0,0,0,0,0,0]):

    locationData.loc[locationData['Store'] == location, 'Group 1'] = group[0]
    locationData.loc[locationData['Store'] == location, 'Group 2'] = group[1]
    locationData.loc[locationData['Store'] == location, 'Group 3'] = group[2]
    locationData.loc[locationData['Store'] == location, 'Group 4'] = group[3]
    locationData.loc[locationData['Store'] == location, 'Group 5'] = group[4]
    locationData.loc[locationData['Store'] == location, 'Group 6'] = group[5]
    
    return locationData

def checkNodeAssignment(locationData,distanceData,startingNodes):
    # loop through each of the nodes to check that it has been assigned to at least one group
    for node in locationData.index:
        groups = locationData.loc[node,'Group 1':'Group 6']
        if (groups.sum() < 1):
            # extracting the row of distances from the starting node
            distances = distanceData.loc[node,startingNodes]
            # sorting the distances
            distances = distances.sort_values()
            # selection the k smallest distances
            closestNodeDistances = distances[0]
            # Extract the group number for the closest node group
            group = [0,0,0,0,0,0]
            group[startingNodes.index(closestNodeDistances.index)] = 1
            # assign to closest group 
            assignNode(locationData, node, group=group)



if __name__ == "__main__":

    # Loading given data.
    distanceData = pd.read_csv('WoolworthsDistances.csv', index_col=0)
    locationData = pd.read_csv('WoolworthsLocations.csv')

    # Initializing grouping columns,
    locationData['Group 1'] = 0
    locationData['Group 2'] = 0
    locationData['Group 3'] = 0
    locationData['Group 4'] = 0
    locationData['Group 5'] = 0
    locationData['Group 6'] = 0

    # Create a list of starting nodes to create groups around based of geographical intuition
    startingNodes = ['Countdown Lynfield','Countdown Manukau Mall','Countdown Henderson','Countdown Highland Park','Countdown Mt Eden','Countdown Milford']

    CreateGroups(distanceData,locationData,startingNodes)

    checkNodeAssignment(locationData,distanceData,startingNodes)


