# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 16:08:58 2015

@author: Suffyan Asad
"""

import MySQLdb
import pandas as pd
from sklearn import decomposition, preprocessing
from scipy.cluster.vq import kmeans,vq

columns = ['country', 'PM2_5', 'CO2Emissions', 'UrbanPopulation']
columnsQuery = ''.join([column + ',' for column in columns])
columnsQuery = columnsQuery[0:(len(columnsQuery) - 1)]
table = 'IndicatorChanges'
query = 'select %s  from %s;' % (columnsQuery, table)

updateQuery = 'update IndicatorChanges set Cluster = %d where country in %s'
numClusters = 5

def GetDataframe(query):
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db='ProjectDb')
    frame = pd.read_sql_query(query, connection)
    connection.close()
    frame = frame.set_index('country')
    return frame

def CreateClusters(dataFrame, numClusters):
    dataFrameScaled = preprocessing.scale(dataFrame)
    
    pca = decomposition.PCA()
    pca.fit(dataFrameScaled)
    
    pca.n_components = 2
    
    dataFrameReduced = pca.fit_transform(dataFrameScaled)
    
    centroids,_ = kmeans(dataFrameReduced,numClusters)
    idx,_ = vq(dataFrameReduced, centroids)
    
    return idx

def UpdateClusters(dataFrame, cluster, countries):
    countries = ''.join(['"%s",' % country for country in countries])
    countries = countries[0:len(countries)-1]
    countries = '('+countries+');'
    query = updateQuery % (cluster, countries)
    
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db='ProjectDb')
    cursor = connection.cursor()
    q = cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

    
dataFrame = GetDataframe(query)
idx = CreateClusters(dataFrame, numClusters)

i = 0;

while i < numClusters:
    print ""
    print "Cluster %d" %i
    print dataFrame[idx==i].describe()
    i += 1

i = 0;

while i < numClusters:
    countries = dataFrame[idx==i].index.values
    UpdateClusters(dataFrame, i, countries)
    i += 1

print ""
print "Table %s updated with cluster numbers" %table



