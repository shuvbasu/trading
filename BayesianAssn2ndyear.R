gammasim<-function(a,b,n){
  rgamma(n,a,b)
}
normalsim<-function(m,v,n){
  rnorm(n,m,v)
}
niter <- 1000
n <- 200
alpha <- 1
beta <- 2
tao <- 1
miu0 <- 0
#Initiliaze miu & Lmabda to 0 & 1 resp, hence X ~ N(0,1)
miu1 <- rep(0,niter) 
lambda1 <- rep(1,niter)
#set.seed(123)
x <- rnorm(n,miu1,lambda1) # Get n random numbers with mean = 0 & Var = 1

for (j in 2:niter) {
  miu_new <- normalsim((tao*miu0 + n*lambda1[j-1]*mean(x))/(tao + n*lambda1[j-1]) , 1/(tao + n*lambda1[j-1]), 1)
  lambda_new <- gammasim(alpha + n/2,beta + 1/2*sum((x - miu1[j-1])^2),1)
  miu1[j] <- miu_new
  lambda1[j] <- lambda_new
}
# Plot the sample now 
par(mfrow=c(2,3))
plot(miu1,ylab="miu", type="l") 
plot(lambda1,ylab="lambda", type="l")
mean(miu1)
mean(lambda1)
library(MASS)
#Plot histograms of miu & lambda 
truehist(miu1, xlab = "miu")
truehist(lambda1, xlab = "lambda")
#Var(Lambda|X)
var(lambda1)