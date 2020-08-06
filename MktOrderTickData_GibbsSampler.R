gammasim<-function(a,b,n){
  rgamma(n,a,b)
}
normalsim<-function(m,v,n){
  rnorm(n,m,v)
}
niter <- 10000
n <- 200
alpha <- 5
beta <- 10
tao <- 1
miu0 <- 0
#Initiliaze miu & Lmabda to 0 & 1 resp, hence X ~ N(0,1)
miu1 <- rep(0,niter) 
# Set Lambda, the Rate param as the Max Likelihood estimate i.e Mean of Volume , sum(volume)/count
#lambda_dax <- 1.79
lambda1 <- rep(2,niter)
set.seed(123)
x <- rpois(n,lambda_dax) # Get n random numbers with mean = 0 & Var = 1

for (j in 2:niter) {
  #miu_new <- normalsim((tao*miu0 + n*lambda1[j-1]*mean(x))/(tao + n*lambda1[j-1]) , 1/(tao + n*lambda1[j-1]), 1)
  lambda_new <- gammasim(alpha + sum(x),beta + n,1)
  #miu1[j] <- miu_new
  lambda1[j] <- lambda_new
}
# Plot the sample now
par(mfrow=c(2,3))
#plot(miu1,ylab="miu", type="l")
plot(lambda1,ylab="lambda")
#mean(miu1)
mean(lambda1)
library(MASS)
#Plot histograms of miu & lambda 
#truehist(miu1, xlab = "miu")
truehist(lambda1, xlab = "lambda")
#Var(Lambda|X)
var(lambda1)