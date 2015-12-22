library(rworldmap)
library(RColorBrewer)
library(RMySQL)

getCountryData <- function(){
  query = "SELECT country, PM2_5, CO2Emissions, UrbanPopulation
           from ProjectDb.IndicatorChanges";

  connection = dbConnect(MySQL(),
                         user='root',
                         password='root',
                         host='localhost',
                         dbname='ProjectDb'
  )
  table = dbGetQuery(conn = connection, statement = query);
  rownames(table) = table$country;
  table <- table[, !names(table) %in% c('country')]
  dbDisconnect(connection);
  table
};

writeToMySql <- function(dataFrame)
{
  connection = dbConnect(MySQL(),
                         user='root',
                         password='root',
                         host='localhost',
                         dbname='ProjectDb'
  )
  dbWriteTable(connection, value = dataFrame, name="HierarchicalClustering", overwrite=TRUE)
  dbDisconnect(connection)
  print ("Clusters saved in table HierarchicalClustering in database ProjectDb")
}

createClustersPlotOnMap <- function(dataFrmae)
{
  colorPal <- brewer.pal(n = 5, name = 'Dark2')
  forMap = cbind(country = rownames(dataFrmae), dataFrmae)
  rownames(forMap) <- NULL;
  mapDevice(device="png", file='HierarchicalClustering.png')
  sPDF <- joinCountryData2Map(forMap, joinCode = "NAME", nameJoinColumn  = "country")
  mapCountryData(sPDF, nameColumnToPlot = "cutTree", 
                 colourPalette = colorPal,
                 missingCountryCol = 'White',
                 borderCol = 'Black',
                 oceanCol = "LightBlue",
                 catMethod = "categorical")
  print ("plot saved as HierarchicalClustering.png")
  dev.off()
}


table = getCountryData();
distMatrix <- dist(table, method='euclidean');
clusterFit <- hclust(distMatrix, method="ward.D");
cutTree = cutree(clusterFit, k=5)
clustersFrame <- data.frame(cutTree);
writeToMySql(clustersFrame)
createClustersPlotOnMap(clustersFrame)



