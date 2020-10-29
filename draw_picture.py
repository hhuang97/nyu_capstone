# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 22:32:05 2020

@author: 王睿
"""

x=x.dropna()
import matplotlib.pyplot as plt
fig = plt.figure()

ax1 = fig.add_subplot(111)
ax1.plot(x.index,x.iloc[:,0],label='S&P',color='r')
plt.legend()
ax2 = ax1.twinx()
ax2.plot(x.index,x.iloc[:,4],label="AAA CLO") 
#change 4 to [1,3], label should be "CDX","Loan Price" to get the other two pictures
plt.legend()
plt.show()
cor_18=x.corr()

y=y.dropna()
import matplotlib.pyplot as plt
fig = plt.figure()

ax1 = fig.add_subplot(111)
ax1.plot(y.index,y.iloc[:,0],label='S&P',color='r')
plt.legend()
ax2 = ax1.twinx()
ax2.plot(y.index,y.iloc[:,4],label="AAA CLO")
#change 4 to [1,3], label should be "CDX","Loan Price" to get the other two pictures
plt.legend()
plt.show()
cor_20=y.corr()

