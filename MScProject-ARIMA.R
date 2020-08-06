library(tseries)
library(car)
require(ggplot2)
library('forecast')
#Datasets#
SP500Dataset<-data.frame(read.csv("C:\\All R Codes\\Datasets\\SPX500_USD.csv", header= TRUE))
GBPUSDDataset<-data.frame(read.csv("C:\\All R Codes\\Datasets\\GBP_USD.csv", header= TRUE))
AUDUSDDataset<-data.frame(read.csv("C:\\All R Codes\\Datasets\\AUD_USD.csv", header= TRUE))


acf(SP500Dataset$closeBid)
par(mfrow=c(2, 3))
plot(SP500Dataset$closeBid)
#Stationarity is achieved by differentiating once
close_diff_SP500 <- diff(SP500Dataset$closeBid)
close_diff_GBPUSD <- diff(GBPUSDDataset$closeBid)
close_diff_AUDUSD <- diff(AUDUSDDataset$closeBid)

par(mfrow=c(3, 2))
plot(SP500Dataset$closeBid)
plot(close_diff_SP500)
plot(GBPUSDDataset$closeBid)
plot(close_diff_GBPUSD)
plot(AUDUSDDataset$closeBid)
plot(diff(close_diff_AUDUSD))
# Significance found at 52 lag !
par(mfrow=c(3, 2))
acf(close_diff_SP500[1:1306], lag.max = 55)
pacf(close_diff_SP500[1:1306], lag.max = 55)
acf(close_diff_GBPUSD[1:1306], lag.max = 55)
pacf(close_diff_GBPUSD[1:1306], lag.max = 55)
acf(close_diff_AUDUSD[1:1306], lag.max = 55)
pacf(close_diff_AUDUSD[1:1306], lag.max = 55)

fitarimaSP500 <- arima(SP500Dataset$closeBid, order = c(29,1,0))
fitarimaSP500_2 <- arima(SP500Dataset$closeBid, order = c(4,1,0))



 