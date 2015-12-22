# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 19:08:18 2015

@author: Suffyan Asad
"""

import MySQLdb
from pandas.io import sql
import cairo; """ sudo apt-get install python-cairo """
import rsvg; """ sudo apt-get install python-rsvg """
import matplotlib.pyplot as plot
import matplotlib.image as mimg
import matplotlib.colors as mcolors
from pylab import bar, legend, savefig
import numpy as np
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("TableName", type=str, help="Name of the table")
parser.add_argument("Start", type=int, help="Start year")
parser.add_argument("End", type=int, help="End Year")
parser.add_argument("-s", '--single', action='store', 
                    type=str, help="whether to use single column")

args = parser.parse_args()

table = args.TableName
startYear = args.Start
endYear = args.End

grey = '#CDCDCD'
colors = ['#008ED5', '#57B0DC', '#76D0FD', '#D2F1FF', '#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#990000']

path_style = 'font-size:12px;fill-rule:nonzero;stroke:#000000;stroke-opacity:1;\
stroke-width:0.2;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;\
marker-start:none;stroke-linejoin:bevel;fill:'

def readDataFrame(table, startYear, endYear):
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db='ProjectDb')
    query = 'select country, round(`%d` - `%d`) as Diff from %s;' % (endYear, startYear, table)

    if (args.single != None):
        query = 'select country, `%s` as Diff from %s;' % (args.single, table)

    dataFrame = sql.read_frame(query, connection)
    dataFrame = dataFrame.sort('Diff', axis=0, ascending=False)

    dataFrame = dataFrame.set_index('country')
    connection.close()
    return dataFrame

def getMinMaxOfDataframe(dataFrame):
    maxDiff = dataFrame.describe().loc[['max']].values[0,0]
    minDiff = dataFrame.describe().loc[['min']].values[0,0]
    
    return [minDiff, maxDiff]

def createBinStrings(bins):
    strings = []
    
    for index, num in enumerate(bins):
        if (index == 0):
            strings.append(('<= %.2f' % num))
        elif (index == (len(bins) - 1)):
            strings.append(('>= %.2f' % num))
        else:
            strings.append('(%.2f, %.2f]' % (num, bins[index+1]))
    
    return strings

def binData(minMax):
    binsNeg = np.linspace(minMax[0], 0, 5)
    binsPos = np.linspace(0, minMax[1], 5)
    bins = np.concatenate((binsNeg, binsPos[1:]))
    
    return bins

def CreateCountriesMapPlot(dataFrame, bins):
    svg = open('worldLow.svg', 'r').read()
    soup = BeautifulSoup(svg, 'lxml')
    paths = soup.findAll('path')
    
    countries = dataFrame.index
    
    for path in paths:
        country = path['title']
        color = grey
        if (country in countries) == True:
            countryValue = dataFrame.loc[country].values[0]
            
            if (countryValue >= bins[8]):
                color = colors[8]
            elif (countryValue >= bins[7]):
                color = colors[7]
            elif (countryValue >= bins[6]):
                color = colors[6]
            elif (countryValue >= bins[5]):
                color = colors[5]
            elif (countryValue >= bins[4]):
                color = colors[4]
            elif (countryValue >= bins[3]):
                color = colors[3]
            elif (countryValue >= bins[2]):
                color = colors[2]
            elif (countryValue >= bins[1]):
                color = colors[1]
            elif (countryValue >= bins[0]):
                color = colors[0]
                
        path['style'] = path_style + color;
            
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1008, 651)
    ctx = cairo.Context(img)
    handle = rsvg.Handle(None, str(soup))
    handle.render_cairo(ctx)
    
    """ write the svg as png image """
    img.write_to_png("plot.png")

def mainProgram():
    
    dataFrame = readDataFrame(table, startYear, endYear)
    
    minMax = getMinMaxOfDataframe(dataFrame)
    
    bins = binData(minMax)  
    strings = createBinStrings(bins)
    
    CreateCountriesMapPlot(dataFrame, bins)
    
    img = mimg.imread("plot.png")
    
    template = []
    
    """ show image """
    plt = plot.imshow(img)
    plt = plot.axis('off')
    for c in colors:
        template.append(bar([0],0, width=0, color=mcolors.hex2color(c), edgecolor='none'))
    
    legend(template, strings, loc=3, prop={'size':8})
    
    fig = plot.gcf()
    
    savefig('%s.png' % table, dpi=300)
    print "Plot Image saved as %s.png" % table

mainProgram()
