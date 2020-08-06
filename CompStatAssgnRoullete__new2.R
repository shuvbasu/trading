# Comp Stat Assignment 2019
# Code to simulate n rolls of a ball
# In number ranges from 1 to 10 and 19 to 28, odd numbers are red and even are black. 
#In ranges from 11 to 18 and 29 to 36, odd numbers are black and even are red.

#set.seed(20)

n= 10
floor(runif(n,1,37))
#Same result
#set.seed(20)
sample(1:37,n,replace = TRUE)
# Simulate 1 roll first
n = 1
sample(1:37,n,replace = TRUE)
pred <- 18/37
pblack <- 18/37
pgreen <- 1/37
red <- c(1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36)
black <- c(2,4,6,8,10,11,15,17,20,22,24,26,28,29,31,33,35)
green <- c(37)
nRoll = 500
nGame = 1000
slots <- c(32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26,37)
rightslots <- c(32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,11,30,8,23,10)
tiltrightprob <-c(0.027,0.027,0.027,0.027,0.028,0.028,0.028,0.0285,0.0285,0.028,0.028,0.028,0.028,0.028,0.028,0.028,0.028,
                  0.027,0.027,0.027,0.02703,0.027,0.027,0.026,0.026,0.026,0.026,0.026,0.026,
                  0.026,0.026,0.026,0.026,0.026,0.027,0.027,0.027,0.027,0.027)



#set.seed(20)
#result <- simulateRoll(n,stratA,stratB,stratC,stratD,betD,amountA,amountB,amountC,amountD,red,black,green)
#print ("Strategy A yields " %% stratA)
#simulateRoll <- function(n,stratA,stratB,stratC,stratD,betD,amountA,amountB,amountC,amountD,red,black,green){
# Initialize the amounts for each strategy for each game
gameamountA <- c();gameamountB <- c();gameamountC <- c();gameamountD <- c(); gameamountTilted <- c();

# The main loop starts . Setting nGame and nRoll gives the desired no. of games & rolls
# Eg: Setting nGame = 1 and nRoll = 1 gives the result for a single roll (Question 2 part 1)
# Setting nGame = 1 and nRoll = 500 gives the result for 500 rolls (Question 2 part 2)
# Setting nGame = 1000 and nRoll = 500 gives the result for Question 3

#Comment 
#set.seed(23)  

for (game in 1:nGame){
  # All strategies starts with Initial amount of $10, and a Profit/Loss = 0
  stratA <- 0; stratB <- 0; stratC <- 0; stratD <- 0; betD <- 10; stratTilted <- 0;
  #amount* arrays hold the running profit/loss after each roll
  amountA <- c();amountB <- c();amountC <- c();amountD <- c(); amountTilted <- c();
    
  for (i in 1:nRoll){
        # Strategy A
        # Strategy B:Pick a random number between 1 - 37
        
        slotB <- floor(runif(1,1,37))
        roll <- sample(1:37,1,replace = TRUE)
        rolltilted  <- sample(slots,1, replace = TRUE, prob = tiltrightprob)
        
        # Computing Strategy A & D at the same time 
        #Since Red slots are used in both Strategy A & D
	  if (roll %in% red){
          stratA <- stratA + 10
          stratD <- stratD + betD
          betD <- betD - 1
        }
        else {
          stratA <- stratA - 10
          stratD <- stratD - betD
          betD <- betD + 1
        }
        
        if (roll == slotB) {
            stratB <- stratB + 350
        }
        else stratB <- stratB - 10
        
        # Strategy3: James Bond
	  # Considering NET profit for all 3 bets
        if (roll %in% 19:36){
          stratC <- stratC + 4
        }     
        if ( roll %in% 13:18){
          stratC <- stratC + 5
        }
	  if ( roll == 37){
          stratC <- stratC + 8
        }
	  if (roll %in% 1:12){
		stratC <- stratC - 10
        }
        
        # Storing the each roll level profit/loss for plotting later
        amountA[i] = stratA
        amountB[i] = stratB
        amountC[i] = stratC
	      amountD[i] = stratD
        
        
	  #Uncomment the below line setting nRoll = 1 to show the result for a simulation of single roll
	  #cat ("Result after 1 roll for Strategy A,B & C ->: ", stratA, stratB, stratC)

	  #Strategy D:Alembert
        if (betD <= 0) {
          break;
        }
        
      }
      
  #cat ("Result after : " ,nRoll, " rolls")
  #stratA; stratB; stratC; stratD
  #cat (" Result after 500 rolls Or early termination for Strategy A,B,C & D ->: ", stratA, stratB, stratC, stratD)
	# Plots of Strategy A,B,C & D
	    #sprintf("No. of rolls -> %s" ,i)
      gameamountA[game] = stratA
      gameamountB[game] = stratB
      gameamountC[game] = stratC
      gameamountD[game] = stratD
      
}


#Tilted table game

for (game in 1:nGame){
  
  stratTilted <- 0;
  amountTilted <- c();
  
  for (i in 1:nRoll){
    # Strategy A
    # Strategy B:Pick a random number between 1 - 37
    
    rolltilted  <- sample(slots,1, replace = TRUE, prob = tiltrightprob)
     
    # Strategy with tilted table: #
    #Bet $5 on the numbers on the right;$4.5 on the left;$0.5 on Green. This is based on the 
    #probability of the roll turning up on the Right, Left and Center
    #We can assume the profits would be in similar inverse proportion
    #Assuming profit would be $2 for right slots , $3 for left slots,and $6 for center
    if (rolltilted %in% rightslots){
      stratTilted <- stratTilted + 5
      
    }else {
      stratTilted <- stratTilted - 5
      if (rolltilted == 37){
        stratTilted <- stratTilted + 8  
        
      }
      else {
        stratTilted <- stratTilted - 0.5  
        stratTilted <- stratTilted + 4.5
      }
      
    }
    amountTilted[i] = stratTilted
  }
  gameamountTilted[game] = stratTilted
}


# Print the Mean and Variance from 1000 games for all 4 strategies
mean(gameamountA);var(gameamountA);max(gameamountA);min(gameamountA)
mean(gameamountB);var(gameamountB);max(gameamountB);min(gameamountB)
mean(gameamountC);var(gameamountC);max(gameamountC);min(gameamountC)
mean(gameamountD);var(gameamountD);max(gameamountD);min(gameamountD)
mean(gameamountTilted);var(gameamountTilted);max(gameamountTilted);min(gameamountTilted)


# This figures corresponds to the last game i.e nth game of nGames = 1000

par(mfrow=c(2,2))
plot(gameamountTilted, xlab = "Game", ylab = "Win/Loss")
legend("topleft",legend = c("TiltedTable","Strat A","Strat B","Strat C","Strat D"),cex=.8,col=c("black","blue","red","green","purple"),pch=c(1:5))
lines(gameamountA, col = 'blue')
lines(gameamountB, col = 'red')
lines(gameamountC, col = 'green')
lines(gameamountD, col = 'purple')
#}


plot(amountA, xlab = "Roll", ylab = "Win/Loss")
legend("topright",legend = c("Strat A","Strat B","Strat C","Strat D"),cex=.8,col=c("black","red","green","purple"),pch=c(1:4))	
lines(amountB, col = 'red')
lines(amountC, col = 'green')
lines(amountD, col = 'purple')

plot(amountTilted, xlab = "Roll", ylab = "Tilted win/loss")