# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 19:21:02 2015

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
from bs4 import BeautifulSoup

table = 'IndicatorChanges'
column = 'Cluster'
countriesCol = 'country'

grey = '#CDCDCD'
colors = ['#667162', '#00BDE4', '#66BB55', '#AF8072', '#FFBC44']
clusters = ['0','1','2','3','4']

path_style = 'font-size:12px;fill-rule:nonzero;stroke:#000000;stroke-opacity:1;\
stroke-width:0.2;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;\
marker-start:none;stroke-linejoin:bevel;fill:'

def readDataFrame():
    connection = MySQLdb.connect(host='localhost', user='root', passwd='root', db='ProjectDb')
    query = 'select %s, %s from %s;' % (countriesCol, column, table)

    dataFrame = sql.read_frame(query, connection)

    dataFrame = dataFrame.set_index('country')
    connection.close()
    
    return dataFrame

def CreateCountriesMapPlot(dataFrame, clusters):
    svg = open('worldLow.svg', 'r').read()
    soup = BeautifulSoup(svg, 'lxml')
    paths = soup.findAll('path')
    
    countries = dataFrame.index
    
    for path in paths:
        country = path['title']
        color = grey
        if (country in countries) == True:
            cluster = dataFrame.loc[country].values[0]
            color = colors[cluster]
                
        path['style'] = path_style + color;
            
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1008, 651)
    ctx = cairo.Context(img)
    handle = rsvg.Handle(None, str(soup))
    handle.render_cairo(ctx)
    
    """ write the svg as png image """
    img.write_to_png("cplot.png")

def mainProgram():
    dataFrame = readDataFrame()
    countries = dataFrame.index.values
    
    CreateCountriesMapPlot(dataFrame, clusters)
    
    img = mimg.imread("cplot.png")
    
    template = []
    
    """ show image """
    plt = plot.imshow(img)
    plt = plot.axis('off')
    for c in colors + [grey]:
        template.append(bar([0],0, width=0, color=mcolors.hex2color(c), edgecolor='none'))
    
    legend(template, clusters + ['No Data'], loc=3, prop={'size':8})
    
    fig = plot.gcf()
    
    savefig('mapclusters.png', dpi=300)
    print "Plot Image saved as mapclusters.png"

mainProgram()


