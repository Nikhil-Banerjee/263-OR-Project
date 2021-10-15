import numpy as np
from numpy.core.fromnumeric import mean
import pandas as pd
from random import betavariate

def get_mult(traffic):
    '''
    Generates a random variate from normal distribution 

    Inputs:
        traffic (Pandas Dataframe)
            - dataframe containing traffic congestion data
    Outputs:
        dist (Integer)
            - random variate from normal distribution
    '''
    dist = np.random.normal(np.std(traffic))

    return dist

def pert(a,b,c,*, lamb=4):
    '''
    Generates a random variate from pert distribution 

    Inputs:
        a (Integer)
            - min in data set
        b (Integer)
            - average of data set
        c (Integer)
            - max in data set
    '''
    r = c - a
    alpha = 1 + lamb * (b - a) / r
    beta = 1 + lamb * (c - b) / r
    return a + betavariate(alpha, beta) * r

def findmax(list):
    '''
    Finds max value in dataframe

    Inputs:
        list (numpy 2D array)
            - numpy 2D array containing data values
    Outputs:
        max (Integer)
            - max value in 2D numpy array
    '''

    max = list[0][0]
    for i in range(0,list.shape[0]):
        for j in range(0,list.shape[1]):
            if list[i][j] > max:
                max = list[i][j]
    return max

def findmin(list):
    '''
    Finds min value in dataframe

    Inputs:
        list (numpy 2D array)
            - numpy 2D array containing data values
    Outputs:
        min (Integer)
            - min value in 2D numpy array
    '''
    min = list[0][0]
    for i in range(0,list.shape[0]):
        for j in range(0,list.shape[1]):
            if list[i][j] < min:
                min = list[i][j]
    return min

def findavg(list):
    '''
    Finds avg value in dataframe

    Inputs:
        list (numpy 2D array)
            - numpy 2D array containing data values
    '''
    sum = 0
    count = 0
    for i in range(0,list.shape[0]):
        for j in range(0,list.shape[1]):
                sum += list[i][j]
                count += 1
    return sum/count

if __name__ == "__main__":
    mults = []
    #Testing code
    congestion = pd.read_csv('AKL_congestion.csv', index_col=0)

    weekday_8am = (congestion[["8am","9am","10am","11am"]]).loc["Mon":"Fri"]
    weekday_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Mon":"Fri"]
    weekend_8am = (congestion[["8am","9am","10am","11am"]]).loc["Sat":"Sun"]
    weekend_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Sat":"Sun"]
    
    a = findmin(weekday_8am.to_numpy())
    b = findavg(weekday_8am.to_numpy())
    c = findmax(weekday_8am.to_numpy())

    arr = [pert(a,b,c) for _ in range(20)]
    
    
    



