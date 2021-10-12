import numpy as np
from numpy.core.fromnumeric import mean
import pandas as pd

def get_mult(traffic):

    dist = np.random.normal(np.mean(traffic),np.std(traffic))

    return dist

if __name__ == "__main__":
    mults = []
    congestion = pd.read_csv('AKL_congestion.csv', index_col=0)

    weekday_8am = (congestion[["8am","9am","10am","11am"]]).loc["Mon":"Fri"]
    weekday_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Mon":"Fri"]
    weekend_8am = (congestion[["8am","9am","10am","11am"]]).loc["Sat":"Sun"]
    weekend_2pm = (congestion[["2pm","3pm","4pm","5pm"]]).loc["Sat":"Sun"]

    for i in range(20):
        mults.append(mean(get_mult(weekday_8am)))
    
    yoza = congestion