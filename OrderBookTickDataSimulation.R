gammasim<-function(a,b,n){
  rgamma(n,a,b)
}

#GBPTick<-read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\TickData\\GBPUSD.csv", header= TRUE)

# Test Orderflow of DAX, Nasdaq & EMini S&P Futures (Source: ATS)
DAXVolume <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\TickData\\DAX-250620-BidAskDeltaTape.csv", header= TRUE)

SP500Volume <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\TickData\\SP500-250620-BidAskDeltaTape.csv", header= TRUE)
NAS100Volume <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\TickData\\Nasdaq100-250620-BidAskDeltaTape.csv", header= TRUE)

#scatter.smooth(GBPTick$Timepart,GBPTick$Bid.volume+GBPTick$Ask.volume)
par(mfrow=c(3, 3))
plot(density(DAXVolume$BuyVolume))
plot(density(DAXVolume$SellVolume))

plot(density(SP500Volume$BuyVolume))
plot(density(SP500Volume$SellVolume))

plot(density(NAS100Volume$BuyVolume))
plot(density(NAS100Volume$SellVolume))

#Plot during busy hours 14:30 - 15:30 
plot(density(DAXVolume$BuyVolume[15205:22401]))
plot(density(DAXVolume$SellVolume[15205:22401]))

#Max Likelihood of poisson distr shows rate(lambda = Sum(events)/N)
rate_poi_busy = sum(DAXVolume$BuyVolume[15205:22401]+DAXVolume$SellVolume[15205:22401])/(22401-15205)
rate_dax_poi_all = sum (DAXVolume$BuyVolume+ DAXVolume$SellVolume)/nrow(DAXVolume)

rate_nas_poi_all = sum (NAS100Volume$BuyVolume+ NAS100Volume$SellVolume)/nrow(NAS100Volume)

rate_sp500_poi_all = sum (SP500Volume$BuyVolume+ SP500Volume$SellVolume)/nrow(SP500Volume)

#cat("ALL MktOrder Volume: DAX, NASDaq, Emini S&P " , rate_poi_all,rate_nas_poi_all, rate_sp500_poi_all)
cat("ALL MktOrder Rate: DAX, NASDaq, Emini S&P " , rate_poi_all,rate_nas_poi_all, rate_sp500_poi_all)
#cat("BUSY Rate" , rate_poi_busy)

# TO VIEW Data corresponding to timestamp
#SP500Volume[SP500Volume$BuyVolume > 10,] 