import numpy as np
from numpy.core.fromnumeric import mean
import pandas as pd
from random import betavariate

def get_mult(traffic):

    dist = np.random.normal(np.std(traffic))

    return dist

def pert(a,b,c,*, lamb=4):
    
    r = c - a
    alpha = 1 + lamb * (b - a) / r
    beta = 1 + lamb * (c - b) / r
    return a + betavariate(alpha, beta) * r

def findmax(list):
    max = list[0][0]
    for i in range(0,list.shape[0]):
        for j in range(0,list.shape[1]):
            if list[i][j] < max:
                max = list[i][j]
    return max

def findmin(list):
    min = list[0][0]
    for i in range(0,list.shape[0]):
        for j in range(0,list.shape[1]):
            if list[i][j] > min:
                min = list[i][j]
    return min

def findavg(list):
    sum = 0
    count = 0
    for i in range(0,list.shape[0]):
        for j in range(0,list.shape[1]):
                sum += list[i][j]
                count += 1
    return sum/count
if __name__ == "__main__":
    mults = []
    congestion = pd.read_csv('AKL_congestion.csv', index_col=0)

    weekday_8am = (congestion[["8am","9am","10am","11am"]]).loc["Mon":"Fri"]
    weekday_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Mon":"Fri"]
    weekend_8am = (congestion[["8am","9am","10am","11am"]]).loc["Sat":"Sun"]
    weekend_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Sat":"Sun"]
    
    a = findmin(weekday_8am.to_numpy())
    b = findavg(weekday_8am.to_numpy())
    c = findmax(weekday_8am.to_numpy())

    arr = [pert(a,b,c) for _ in range(20)]
    
    
    



