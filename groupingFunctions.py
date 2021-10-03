import numpy as np
import pandas as pd
import math
from pulp import *
from routeFunctions import *

def CreateGroups(distanceData,locationData,startingNodes):
    ''' Groups the nodes based on proximity to selected starting nodes.

        Parameters:
        -----------
        locationData : pandas dataframe
                        dataframe containing location data.
        distanceData : pandas dataframe
                        dataframe containing travel time data.
        startingNodes : array
                    string array of starting nodes for each group
        Returns:
        --------
        locationData : pandas dataframe
                        dataframe containing location data updated with additional grouping. 
        Notes:
        --------
        Calls the assignNode function 
    '''
    # initialising number of number of nodes selected for each group 
    k = 10 

    # loop through starting nodes
    for node in startingNodes:
        group = np.zeros(len(startingNodes))
        group[startingNodes.index(node)] = 1
        # extracting the row of distances from the starting node
        distances = distanceData.loc[node,:]
        # sorting the distances
        distances = distances.sort_values()
        # selection the k smallest distances
        closestNodeDistances = distances[:k]
        # extracting names of closest nodes
        for i in closestNodeDistances.index:
            assignNode(locationData, i, group)

    # loop through each of the nodes to check that it has been assigned to at least one group
    for node in locationData.index:
        groups = locationData.loc[node,'Group 1':'Group '+ str(len(startingNodes))]
        if (groups.sum() < 1):
            # extracting the row of distances from the starting node
            distances = distanceData.loc[distanceData.index[node],startingNodes]
            # sorting the distances
            distances = distances.sort_values()
            # selection the k smallest distances
            closestNodeDistance = distances[:1]
            # Extract the group number for the closest node group
            group = np.zeros(len(startingNodes))
            group[startingNodes.index(closestNodeDistance.index)] = 1
            # assign to closest group 
            assignNode(locationData, distanceData.index[node], group=group)

    return locationData


def assignNode(locationData, location, group):
    ''' Assigns a specific location node to an indicated group.

        Parameters:
        -----------
        locationData : pandas dataframe
                        dataframe containing location data.
        location : string 
                    name of the node being assigned.
        group : array
                    binary array indicating which group the node is being assigned to.
    '''
    for i in range(len(group)):
        if (group[i] == 1):
            locationData.loc[locationData['Store'] == location, 'Group '+str(i+1)] = 1


if __name__ == "__main__":

    # Loading given data.
    distanceData = pd.read_csv('WoolworthsDistances.csv', index_col=0)
    locationData = pd.read_csv('WoolworthsLocations.csv')

    # Create a list of starting nodes to create groups around based of geographical intuition
    startingNodes = ['Countdown Lynfield','Countdown Manukau Mall','Countdown Henderson','Countdown Highland Park','Countdown Mt Eden','Countdown Milford']

    # Initializing grouping columns
    for i in range(len(startingNodes)):
        locationData['Group '+ str(i+1)] = 0
    
    # Apply grouping function
    GroupedLocations = CreateGroups(distanceData,locationData,startingNodes)

    # Export grouping information to csv
    GroupedLocations.to_csv('GroupedLocations.csv')


