import numpy as np
import pandas as pd
from pulp import *


def loadDemands():
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


if __name__ == "__main__":
    
    demands = loadDemands()

    truckCost = 3.75 # per minute (225/60 = 3.75)
    truckFleet = 30
    truckCapacity = 26

    unloadTime = 7.5 # in minutes


    probWkDay = LpProblem("Week Day LP", LpMinimize)

    



    
    pass