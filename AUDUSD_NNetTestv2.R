library("e1071")
library(car)
library(ggplot2)
library(MASS)
library(nnet)
GBPUSD_D<-read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\GBPUSD_D_SVMTraining_CloseChange5.csv", header = TRUE)
TrainingOutput_D<-read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\TrainingOutput_All.csv", header= TRUE)
summary(GBPUSD_D)
GBPUSD_D_TestData <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\GBPUSD_D_SVMTestGrid2.csv", header= TRUE)

# Normalize the Data
#GBPUSD_D_normalized<-read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\GBPUSD_D_SVMTraining_CloseChange_NormalizedV1.csv", header = TRUE)
#GBPUSD_D_TestData_normalized <- data.frame(read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\GBPUSD_D_SVMTestGrid_normalized.csv", header= TRUE))
GBPUSD_D_normalized <- scale(GBPUSD_D)

GBPUSD_D_TestData_normalized <- scale(GBPUSD_D_TestData)


#AUDUSD Training & Test data
AUDUSD_D <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\AUD_USD_D_SVMTraining2.csv", header = TRUE)
AUDUSD_D_TestData <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\AUDUSD_D_SVMTestGrid2.csv", header = TRUE)

AUDUSD_D_normalized <- scale(AUDUSD_D)
AUDUSD_D_TestData_normalized < - scale(AUDUSD_D_TestData)

#TEst Data to tune:

TestData <- read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\SVM_TestData_ALL.csv", header = TRUE)



#Show the pairwise corr
#scatterplotMatrix(GBPUSD_D) 


x <- matrix(data = GBPUSD_D, nrow = 469, ncol = 16)
x_GBPUSD_normalized <- matrix(data = GBPUSD_D_normalized, nrow = 469, ncol = 16)
#Pick the Dependant variable as a Numeric value, not Boolean !
y_GBPUSD <- TrainingOutput_D$GBPTrendNumeric
#Construct the Data frame with the Output & Inputs
GBPUSD_D_normalized_df <- data.frame(y_GBPUSD, GBPUSD_D_normalized)
y_reg <- TrainingOutput_D$closeChange
x_test <- matrix(data = GBPUSD_D_TestData_normalized, nrow = 258, ncol = 16)

x_AUDUSD <- matrix(data = AUDUSD_D, nrow = 469, ncol = 16)
y_AUDUSD_reg <- TestData$AUDUSD
y_AUDUSD <- TrainingOutput_D$AUDTrendNumeric
x_test_AUDUSD <- matrix(data = AUDUSD_D_TestData, nrow = 258, ncol = 16)
AUDUSD_D_normalized_df <- data.frame(y_AUDUSD, AUDUSD_D_normalized)


tuneObj_GBP_nnet<-tune(nnet, y_GBPUSD ~., data = GBPUSD_D_normalized_df, ranges = list(decay = seq(from = 0.1, to = 0.5, by = 0.1),
                                                                    size = seq(from = 3, to = 10, by = 1)))
tuneObj_GBP_nnet
tuneObj_AUD_nnet<-tune(nnet, y_AUDUSD ~., data = AUDUSD_D_normalized_df, ranges = list(decay = seq(from = 0.1, to = 0.5, by = 0.1),
                                                                    size = seq(from = 3, to = 10, by = 1)))
# Found: decay =0.3, size = 4
tuneObj_AUD_nnet

#Do SVM classification based on Close price change , +ve or -ve; On Normalized and Non-Normalized data
svmfitGBP_normalized <- svm(TrainingOutput_D$TREND ~ . ,data = GBPUSD_D_normalized, kernel = "radial", cost = 4,gamma= 0.5, 
              type = "C-classification")
summary(svmfitGBP_normalized)

# Perform Neural Net based on previous Tuning output
nnetfitGBP_normalized <- nnet(y_GBPUSD ~ . ,data = GBPUSD_D_normalized_df, size = 7, decay = 0.2)
summary(nnetfitGBP_normalized)

nnetfitAUD_normalized <- nnet(y_AUDUSD ~ . ,data = AUDUSD_D_normalized_df, size = tuneObj_AUD_nnet$best.parameters$size, decay = tuneObj_AUD_nnet$best.parameters$decay)
summary(nnetfitAUD_normalized)

#GBPUSD Non-Normalized data
svmfitGBP1 <- svm(TrainingOutput_D$TREND ~ . ,data = GBPUSD_D, kernel = "radial", cost = 4,gamma= 0.5, 
                            type = "C-classification")
summary(svmfitGBP1)




svmfitAUD <- svm(y_AUDUSD ~ . ,data = x_AUDUSD, kernel = "radial", cost = 4,gamma= 0.5, 
              type = "C-classification")

summary(svmfit_AUD)
#Do SVM Regression based on Close Price change
svmfit_reg <- svm(y_reg ~ . ,data = GBPUSD_D, kernel = "radial", cost = 4,gamma= 0.5)
summary(svmfit_reg)
              

#Run basic Linear regression
linear <- lm(TrainingOutput_D$closeChange ~ ., data = GBPUSD_D)
summary(linear)

#Try Loess Non-parametric regression
loessReg <- gam(TrainingOutput_D$closeChange ~ ., data = GBPUSD_D)
summary(loessReg)

plot(TrainingOutput_D$closeChange, GBPUSD_D$highChange)
#lines(GBPUSD_D$closeChange, GBPUSD_D$LowChange, type = 'l')
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
# RESULT : 138 out of 258 records correctly classified, 54.2% !!

GBPUSD_D_TestData_normalized <- data.frame(read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\GBPUSD_D_SVMTestGrid_normalized.csv", header= TRUE))
pred <- predict(svmfitGBP_normalized,newdata = GBPUSD_D_TestData_normalized)
pred_samedata <- predict(svmfit,newdata = GBPUSD_D)
pred_reg <- predict(svmfit_reg,newdata = GBPUSD_D)
summary(pred)
summary(pred_reg)
#Writing to Output file
write.table(pred, file = "C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\Output_SVM_classification_normalized.csv", sep = ",")
write.table(pred_reg, file = "C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\Output_SVM_regression3_normalized.csv", sep = ",")

# Plot the predicted vs Actual
#1) comparsion: Test dataset same as Training
#2) comparsion2: Diff datset Test vs Training
comparison <- data.frame(read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\GBPUSD_D_SVMTraining3_Trend.csv", header= TRUE))
closechange < - comparison$CloseChange

comparison2 <- data.frame(read.csv("C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\ActualResult.csv", header= TRUE))


# Do the Neural net prediction now
#GBPUSD Nnet pred
# Based on 65% probability Output, 
nnetpred <- predict(nnetfitGBP_normalized, GBPUSD_D_TestData_normalized)
write.table(nnetpred, file = "C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\Output_NNet_classification_normalized2.csv", sep = ",")

#AUDUSD NNet pred
nnetpredAUD <- predict(nnetfitAUD_normalized, scale(AUDUSD_D_TestData), type = "class")
write.table(nnetpredAUD, file = "C:\\Users\\Shuv\\Documents\\All Trading\\Market Data\\Research Data\\Output_AUDNNet_classification_normalized2.csv", sep = ",")


