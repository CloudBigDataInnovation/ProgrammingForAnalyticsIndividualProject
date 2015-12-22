# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 15:58:45 2015

@author: Suffyan Asad
"""

import wbdata as wb
import datetime as dt
import pandas as pd
import argparse
import MySQLdb
from pandas.io import sql

parser = argparse.ArgumentParser()
parser.add_argument("Indicator", type=str, help="Indicator to download from wbdata")
parser.add_argument("DatabaseName", type=str, help="Database Name")
parser.add_argument("TableName", type=str, help="Table name in database")
parser.add_argument("Years", type=int, nargs='+', help="years to download an indicator")

args = parser.parse_args()

databaseName = args.DatabaseName

indicator = {args.Indicator : args.TableName}
table = args.TableName
years = args.Years

years = [dt.datetime(year, 1, 1) for year in years]

def cleanAndReduceDataFrame(dataframe):
    dataframe = dataframe.drop(dataframe.index[0:34])
    dataframe = dataframe.dropna()
    return dataframe

def getDataOverYears(indicator, years):
    dataFrame = wb.get_dataframe(indicator, data_date = years[0])
    dataFrame = cleanAndReduceDataFrame(dataFrame)
    colname = str(years[0].year)
    dataFrame.columns = [colname]
    
    for index, year in enumerate(years[1:]):
        frame = cleanAndReduceDataFrame(wb.get_dataframe(indicator, 
                                                       data_date = years[index+1]))
        colname = str(years[index+1].year)
        frame.columns = [colname]
        dataFrame = pd.concat([dataFrame, frame], axis = 1, join='inner')
    
    return dataFrame

def saveInDb(dataFrame, connection, tableName):
    sql.write_frame(dataFrame, con=connection, name=tableName, if_exists='replace', flavor='mysql')

def mainFunction():
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db=databaseName)
    dataFrame = getDataOverYears(indicator, years)
    dataFrame = dataFrame.reset_index()
    saveInDb(dataFrame, connection, table)
    print "data ", indicator.keys()[0], " saved in table ", table, " in database ", databaseName
    connection.close()
    
mainFunction()

