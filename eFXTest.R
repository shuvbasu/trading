library(tseries)
require("e1071")
library(nnet)
eurusd_df = read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\eFX Test\\RegEurUsd.csv", header= TRUE)
#Try a GLM
#eurusd_df['logratio'] = log(eurusd_df$bidQuantity/eurusd_df$offerQuantity)
#eurusd_df['totalXnetQuantity'] = eurusd_df$totalQuantity*eurusd_df$netQuantity
eurusd_df_x = eurusd_df[,c(9,10,12,13,15)]
#eurusd_df_x = data.frame(scale(eurusd_df_x))
#eurusd_df_y = eurusd_df['midPrice']
#Run the GLM on T+1 Midprice on T0 variates
model2 = glm(eurusd_df$midPrice[2:nrow(eurusd_df)] ~ ., data = eurusd_df_x[1:nrow(eurusd_df_x)-1,])
# T+5
model3 = glm(eurusd_df$midPrice[5:nrow(eurusd_df)] ~ ., data = eurusd_df_x[1:nrow(eurusd_df_x)-4,])
summary(model2)
#Now do the ANOVA
anova(model2)

summary(model3)
#Now do the ANOVA
anova(model3)

# Do the stationarity and ARIMA modelling
diffeurusd = diff(eurusd_df$midPrice)
plot(diffeurusd) # Plot looks fairly stationary
adf.test(diffeurusd)

par(mfrow=c(2, 2))
acf(diffeurusd , lag.max = 300)
pacf(diffeurusd, lag.max = 300)
