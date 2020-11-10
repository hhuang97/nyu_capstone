# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 22:32:05 2020

@author: 王睿
"""

from data_parser import get_all_data, get_2018_data, get_2020_data
import matplotlib.pyplot as plt
import os

x = get_2018_data()
y = get_2020_data()
z = get_all_data()

GRAPH_PATH='plots/sp_graph'

#initial correlation analysis

def sp_rel_graph(data,credit_type,year,save=True):
    x=data.dropna()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x.index,x['SPX_Index'],label='S&P',color='r')
    plt.legend()
    ax2 = ax1.twinx()
    ax2.plot(x.index,x[credit_type],label=credit_type)
    #change 4 to [1,3], label should be "CDX","Loan Price" to get the other two pictures
    plt.legend()
    if save:
        plt.savefig(GRAPH_PATH+'/{}.png'.format(year+credit_type))



if __name__ == '__main__':
    # 4 is "AAA CLO"
    #change 4 to [1,3], label should be "CDX","Loan Price" to get the other two pictures
    credits = x.columns
    # for i in credits[1:]:
    #     sp_rel_graph(x,i,'2018')
    #     sp_rel_graph(y,i,'2020')

    cor_year_2018 = x.corr()
    cor_year_2018.to_csv('data/2018correlation.csv')
    cor_year_2020 = y.corr()
    cor_year_2020.to_csv('data/2020correlation.csv')



