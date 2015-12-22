# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 21:18:20 2015

@author: SuffyanAsad
"""

import MySQLdb
import pandas as pd
import argparse
import matplotlib.pyplot as plot
from pylab import savefig
import numpy as np
from pandas.io import sql

parser = argparse.ArgumentParser()
parser.add_argument("Table1", type=str, help="First Table")
parser.add_argument("Table2", type=str, help="Second Table")
parser.add_argument("PlotName", type=str, help="Name of plot image")
parser.add_argument("-c", "--country", action='store_true', help="Country-wise comparison")
parser.add_argument("Years", type=int, nargs='+', help="years to include in correlaton")

args = parser.parse_args()

table1Name = args.Table1
table2Name = args.Table2

years = args.Years

databaseName = "ProjectDb"

def GetDataSet(tableName, years):
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db='ProjectDb')

    query = ''.join(['AVG(`%d`) as `%d`,' % (year, year) for year in years])
    query = 'select %s from %s' % (query[:len(query)-1], tableName)
    
    frame = pd.read_sql_query(query, connection)

    connection.close()
    return frame

def GetCountryWiseDataSet(tableName, years):
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db='ProjectDb')

    query = ''.join(['`%d`,' % (year) for year in years])
    query = 'select country, %s from %s' % (query[:len(query)-1], tableName)
    frame = pd.read_sql_query(query, connection)

    connection.close()
    return frame

def PrintAndPlotAvgCorrelation():
    frame1 = GetDataSet(table1Name, years)
    frame2 = GetDataSet(table2Name, years)
    
    print table1Name
    print frame1.loc[0]
    print ""
    print table2Name
    print frame2.loc[0]
    print 'Correlation between %s and %s is: %f' %(table1Name, table2Name, frame1.loc[0].corr(frame2.loc[0]))
    
    fig, ax = plot.subplots()
    plt = ax.scatter(frame1.loc[0].values, frame2.loc[0].values)
    plot.xlabel(table1Name)
    plot.ylabel(table2Name)
    
    for index, year in enumerate(years):
        ax.annotate(year, [frame1.loc[0].values[index], frame2.loc[0].values[index]])
    
    savefig("%s.png" % args.PlotName)
    print ""
    print "plot saved as %s.png" % (args.PlotName)

def flattenDataFrame(passedFrame, tableName):
    flatDataFrame = pd.DataFrame()    
    
    for country in passedFrame.country.values:
        values = passedFrame.loc[passedFrame['country'] == country].values[0][1:]
        countries = [country] * len(years)
        frame = pd.DataFrame(values, [years, countries])
        frame = frame.reset_index()
        frame.columns =['year', 'country', tableName]
        
        flatDataFrame = pd.concat([flatDataFrame, frame])
        
    flatDataFrame = flatDataFrame.set_index(['year', 'country'])
    return flatDataFrame

def GetCountryWiseCorrelation():
    frame1 = GetCountryWiseDataSet(table1Name, years)
    frame2 = GetCountryWiseDataSet(table2Name, years)
    
    countries = np.intersect1d(frame1.country.values, frame2.country.values)
    
    correlations = pd.DataFrame()    
    
    for country in countries:
        series1 = pd.Series(float(val) for val in frame1.loc[frame1.country == country].values[0][1:])
        series2 = pd.Series(float(val) for val in frame2.loc[frame2.country == country].values[0][1:])     
        
        correlation = series1.corr(series2)
        
        frame = pd.DataFrame([correlation], [country])
        
        correlations = pd.concat([correlations, frame])
    
    correlations = correlations.dropna()
    correlations.columns = ['correlation']
    correlations = correlations.sort('correlation')
    
    print "10 highest correlations"
    print correlations.tail(10)    
    
    print ""
    print "10 lowest correlations"
    print correlations.head(10) 
    
    tableName = 'correlation_%s_%s' % (table1Name, table2Name)
    
    correlations = correlations.reset_index()
    correlations.columns = ['country', 'correlation']
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db=databaseName)
    sql.write_frame(correlations, con=connection, name=tableName, if_exists='replace', flavor='mysql')
    connection.close()
    
    print "correlations saved in: " + tableName

def PrintAndPlotIndividualCorrelation():
    frame1 = GetCountryWiseDataSet(table1Name, years)
    frame2 = GetCountryWiseDataSet(table2Name, years)
    
    flatDataFrame1 = flattenDataFrame(frame1, table1Name)
    
    flatDataFrame2 = flattenDataFrame(frame2, table2Name)
    
    finalFrame = pd.concat([flatDataFrame1, flatDataFrame2], axis = 1, join = 'inner')
    
    fig, ax = plot.subplots()
    
    plt = ax.scatter(finalFrame[table1Name].values, finalFrame[table2Name].values)
    plot.xlabel(table1Name)
    plot.ylabel(table2Name)
    
    savefig("%s.png" % args.PlotName)
    print ""
    print "plot saved as %s.png" % (args.PlotName)
    print ""

if (args.country == True):
    PrintAndPlotIndividualCorrelation()
    GetCountryWiseCorrelation()
else:
    PrintAndPlotAvgCorrelation()