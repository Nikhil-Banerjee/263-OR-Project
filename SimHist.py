import seaborn as sns
import pickle
import matplotlib.pyplot as plt
import numpy as np


with open('savedWkDaySim.pkl','rb') as f:
    WeekdayCost = pickle.load(f)

with open('savedWkDayRemSim.pkl','rb') as f:
    WeekdayCostRem = pickle.load(f)

with open('savedSatDaySim.pkl','rb') as f:
    satCost = pickle.load(f)

with open('savedSatDayRemSim.pkl','rb') as f:
    satCostRem = pickle.load(f)


f1, ax1 = plt.subplots(1,2)
sns.distplot(WeekdayCost, ax=ax1[0], kde=False,label = 'All stores open')
sns.distplot(WeekdayCostRem, ax=ax1[0], kde=False,label = 'After Store Removal').set(title = "Weekday Cost of Operations Distribution", xlabel = 'Cost per day ($)', ylabel = 'Frequency')
ax1[0].legend()

WeekdayCost.sort()
ax1[0].axvline(WeekdayCost[25])
ax1[0].text(WeekdayCost[25]+1,1, '95% CI', rotation = 90, color = 'blue')

ax1[0].axvline(WeekdayCost[975])
ax1[0].text(WeekdayCost[975]+1,1, '95% CI', rotation = 90, color = 'blue')

WeekdayCostRem.sort()
ax1[0].axvline(WeekdayCostRem[25], color = 'orange')
ax1[0].text(WeekdayCostRem[25]+1,1, '95% CI', rotation = 90, color = 'orange')

ax1[0].axvline(WeekdayCostRem[975], color = 'orange')
ax1[0].text(WeekdayCostRem[975]+1,1, '95% CI', rotation = 90, color = 'orange')

# f2, ax1[1] = plt.subplots()
sns.distplot(satCost, ax=ax1[1], kde=False,label = 'All stores open')
sns.distplot(satCostRem, ax=ax1[1], kde=False,label = 'After Store Removal').set(title = "Saturday Cost of Operations Distribution", xlabel = 'Cost per day ($)', ylabel = 'Frequency')
ax1[1].legend()

satCost.sort()
ax1[1].axvline(satCost[25])
ax1[1].text(satCost[25]+1,1, '95% CI', rotation = 90, color = 'blue')

ax1[1].axvline(satCost[975])
ax1[1].text(satCost[975]+1,1, '95% CI', rotation = 90, color = 'blue')

satCostRem.sort()
ax1[1].axvline(satCostRem[25], color = 'orange')
ax1[1].text(satCostRem[25]+1,1, '95% CI', rotation = 90, color = 'orange')

ax1[1].axvline(satCostRem[975], color = 'orange')
ax1[1].text(satCostRem[975]+1,1, '95% CI', rotation = 90, color = 'orange')

print('---------------------------------------------------------')
print('For all stores:')
print("Weekday average cost: ", np.mean(WeekdayCost))
print("Saturday average cost: ", np.mean(satCost))
print("Weekday interval", WeekdayCost[25], " to ", WeekdayCost[975])
print("Saturday interval", satCost[25], " to ", satCost[975])
print('---------------------------------------------------------')
print('For all stores:')
print("Weekday average cost: ", np.mean(WeekdayCostRem))
print("Saturday average cost: ", np.mean(satCostRem))
print("Weekday interval", WeekdayCostRem[25], " to ", WeekdayCostRem[975])
print("Saturday interval", satCostRem[25], " to ", satCostRem[975])
print('---------------------------------------------------------')


plt.show()

