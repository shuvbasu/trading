require("e1071")
require("car")
library(car)
library(ggplot2)
library(tidyr)
GBPUSD_D<-data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/GBPUSD_D_SVMTraining_CloseChange5.csv", header = TRUE))
TrainingOutput_D<-read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/GBPUSD_D_SVMTraining3_Trend.csv", header= TRUE)
summary(GBPUSD_D)
GBPUSD_D_TestData <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/GBPUSD_D_SVMTestGrid2.csv", header= TRUE))


#S&P500
SP500_D <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/SPX500_USD_2.csv", header = TRUE))

#SP500_D_TestData <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/AUDUSD_D_SVMTestGrid2.csv", header = TRUE))



#AUDUSD Training & Test data
AUDUSD_D <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/AUD_USD_D_SVMTraining2.csv", header = TRUE))
AUDUSD_D_TestData <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/AUDUSD_D_SVMTestGrid2.csv", header = TRUE))

#TEst Data to tune:

TestData <- read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/SVM_TestData_ALL.csv", header = TRUE)



#Show the pairwise corr
#scatterplotMatrix(GBPUSD_D) 


x <- matrix(data = GBPUSD_D, nrow = 469, ncol = 16)
y_GBPUSD <- as.factor(TrainingOutput_D$TREND)
y_reg <- TrainingOutput_D$closeChange
x_test <- matrix(data = GBPUSD_D_TestData, nrow = 258, ncol = 16)

x_AUDUSD <- matrix(data = AUDUSD_D, nrow = 469, ncol = 16)
y_AUDUSD_reg <- TrainingOutput_D$AUDUSD
y_AUDUSD <- as.factor(TrainingOutput_D$TrendAUD)
x_test_AUDUSD <- matrix(data = AUDUSD_D_TestData, nrow = 258, ncol = 16)


x_SPX500 <- matrix(data = SP500_D[,-1], nrow = 729, ncol = 15)
y_SPX500_reg <- (diff(SP500_D$closeBid) > 0)
x_test_AUDUSD <- matrix(data = AUDUSD_D_TestData, nrow = 258, ncol = 16)

obj<-tune(svm, y_reg ~., data = GBPUSD_D, ranges = list(gamma = 2^(-2:2), cost = 2^(1:4)))
obj
objAUD <-tune(svm, y_AUDUSD_reg ~., data = AUDUSD_D, ranges = list(gamma = 2^(-3:3), cost = 2^(1:4)))
objAUD

#Do SVM classification based on Close price change , +ve or -ve
svmfit2 <- svm(y_reg ~ . ,data = GBPUSD_D, kernel = "radial", cost = 4,gamma= 0.5
              )
summary(svmfit2)

svmfitAUD <- svm(y_AUDUSD_reg ~ . ,data = AUDUSD_D, kernel = "radial", cost = 5,gamma= 0.3
              )
summary(svmfitAUD)
#Do SVM Regression based on Close Price change
svmfit_reg <- svm(y_AUDUSD_reg ~ . ,data = AUDUSD_D, kernel = "radial", cost = 4,gamma= 0.5)
print(svmfit_reg)
              
# Run SPX500 regression
spxvariates <- SP500_D[,-1][-730,] # This line picks up the dataset omitting the 1st column 'closeBId' which is the y,
# and then ommitts the last row of the dataset to match the same no. of elements of y and x

objSPX <-tune(svm, y_SPX500_reg ~., data = spxvariates, 
              ranges = list(gamma = 2^(-3:3), cost = 2^(1:4),type = "C-classification"))

svmfit_reg_spx500 <- svm(y_SPX500_reg ~ . , data = spxvariates, kernel = "radial", 
                         cost = 50, gamma= 0.5, type = "C-classification", scale = TRUE)
print(svmfit_reg_spx500)

#Run basic Linear regression
linear <- lm(TrainingOutput_D$closeChange ~ ., data = GBPUSD_D)
summary(linear)

#AUD Linear Reg
linearAUD <- lm(TrainingOutput_D$AUDUSD ~ ., data = AUDUSD_D)
summary(linearAUD)

plot(TrainingOutput_D$closeChange, GBPUSD_D$highChange)
lines(TrainingOutput_D$closeChange, GBPUSD_D$rsiChange, type = 'l')
lines(TrainingOutput_D$closeChange, GBPUSD_D$closeW.ema8, type = 'l')

ggplot(data = GBPUSD_D, aes(x=GBPUSD_D$closeChange), scale_colour_manual(values=c("black", "orange")) 
                            ) + geom_line(aes(y= GBPUSD_D$rsiChange, colour = rsiChange)) 
+ geom_line(aes(y= GBPUSD_D$LowChange, colour = LowChange )) 



scatterplotMatrix(data.frame(TrainingOutput_D$closeChange, GBPUSD_D$rsiChange, GBPUSD_D$LowChange,
                             GBPUSD_D$highChange,GBPUSD_D$closeW.ema8))

beta <- drop(t(svmfit$coefs) %*% x[svmfit$index, ])
beta0 <- svmfit$rho


  

#pdf("sim2.pdf")
# plot(x,y,pch=y+18,cex=1.5,cex.axis=1.5,cex.lab=1.5)
# abline(beta0/beta[2],-beta[1]/beta[2])
# abline((beta0-1)/beta[2],-beta[1]/beta[2],lty=2)
# abline((beta0+1)/beta[2],-beta[1]/beta[2],lty=2)

# Try prediction
# RESULT : 138 out of 258 records correctly classified, 53.4% !!

GBPUSD_D_TestData <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/GBPUSD_D_SVMTestGrid2.csv", header= TRUE))
pred <- predict(svmfit,newdata = GBPUSD_D_TestData)
pred_samedata <- predict(svmfit,newdata = GBPUSD_D)
pred_reg <- predict(svmfit_reg,newdata = GBPUSD_D)
summary(pred)
summary(pred_reg)
#Writing to Output file
write.table(pred, file = "/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/Output_SVM_classification.csv", sep = ",")
write.table(pred_reg, file = "/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/Output_SVM_regression3_normalized.csv", sep = ",")

# Plot the predicted vs Actual
#1) comparsion: Test dataset same as Training
#2) comparsion2: Diff datset Test vs Training
comparison <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/GBPUSD_D_SVMTraining3_Trend.csv", header= TRUE))
closechange < - comparison$CloseChange

comparison2 <- data.frame(read.csv("/Users/Shuvadip_Barcap/Documents/MSc-Stat/Stat-R-codes/Research Data/ActualResult.csv", header= TRUE))


cl <- rainbow(5)
plot.default(comparison$No, comparison$closeChange, type = 'l', col = "red")
lines(comparison$fitted, col = "green")

ggplot(data = GBPUSD_D, aes(x=GBPUSD_D$closeChange), scale_colour_manual(values=c("black", "orange")) 
) + geom_line(aes(y= GBPUSD_D$rsiChange, colour = rsiChange)) 
