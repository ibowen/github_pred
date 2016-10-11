setwd("~/Documents/Github/github_pred/")
user0 <- read.csv('data/user_output-0.csv',header=TRUE)
user1 <- read.csv('data/user_output-1.csv',header=TRUE)
user2 <- read.csv('data/user_output-2.csv',header=TRUE)
user3 <- read.csv('data/user_output-3.csv',header=TRUE)
user4 <- read.csv('data/user_output-4.csv',header=TRUE)
user5 <- read.csv('data/user_output-5.csv',header=TRUE)
user6 <- read.csv('data/user_output-6.csv',header=TRUE)
user7 <- read.csv('data/user_output-7.csv',header=TRUE)
user8 <- read.csv('data/user_output-8.csv',header=TRUE)
user9 <- read.csv('data/user_output-9.csv',header=TRUE)

user <- rbind(user0,user1,user2,user3,user4,user5,user6,user7,user8,user9)

# normalized weight for followers
# 5% 10% 50% 90% 95% 
# 0   0   3  22  41 
user$weight_follower <- ifelse(user$followers <= 0, 0, ifelse(user$followers > 41,1, (user$followers)/41))

# normalized weight for public repos
# 5% 10% 50% 90% 95% 
# 0   1   9  44  67 
user$weight_repo <- ifelse(user$public_repos <= 0, 0, ifelse(user$public_repos > 67, 1, (user$public_repos)/67))

write.table(user,file="user_weights.csv",sep=",",quote=FALSE,row.names=FALSE,col.names=TRUE)