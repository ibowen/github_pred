library(scales)
library(ggplot2)

setwd('/home/matthew/Documents/Github/github_pred')
data = read.csv('data/repositories.csv', header=TRUE)
names(data) <- c('id','repo','stars','created_at','updated_at')
data$created_at <- as.character(data$created_at)
data$updated_at <- as.character(data$updated_at)
head(data)
str(data)


# GRAPH 1
# ECDF of repo stars
data.stars.ecdf <- ecdf(data$stars)
plot(data.stars.ecdf, xlab = 'Sample quantiles of stars', ylab = '', main = 'Accumulated Distribution of Sampled Github Repo Stars')
mtext(text = expression(hat(F)[n](x)), side = 2, line = 2.5)
dev.off()

# GRAPH 2
# histrogram of stars
summary(data$stars)
hist(data$stars, xlim=c(0,500),breaks = 10000, col='red', xlab="Number of Stars", main="Distribution of Sampled Github Repo Stars")


# transform of dates variables
data$created_at_date <- as.Date(substr(data$created_at, 0, 10))
data$updated_at_date <- as.Date(substr(data$updated_at, 0, 10))

# GRAPH 3-1
ggplot(data, aes(x=created_at_date)) + 
  stat_bin(binwidth=5, position="identity", fill="blue") + 
  scale_x_date(breaks=date_breaks(width="3 months")) +
  theme(axis.text=element_text(size=10),
        axis.title=element_text(size=12,face="bold"))

# GRAPH 3-2
min_date = as.Date('2015-01-01')
max_date = as.Date('2016-10-01')
ggplot(data, aes(x=updated_at_date)) + 
  stat_bin(binwidth=5, position="identity", fill="blue") + 
  scale_x_date(breaks=date_breaks(width="3 months"), limits=c(min_date,max_date)) + 
  scale_y_continuous(limits=c(0,1000)) +
  theme(axis.text=element_text(size=10),
        axis.title=element_text(size=12,face="bold"))

# GRAPH 4
# scatter plot of stars vs created_at
plot(data$created_at_date, data$stars)
plot(data$updated_at_date, data$stars, xlab="updated_at", ylab="Number of Stars", 
     main="Trend of stars based on most recent update_at date", ylim = c(0,5000), col="red")

# filter 
# get repos with updates in the last month
most_recent_point <-as.Date('2016-08-01')
filtered <- data[which(data$updated_at_date > most_recent_point),]
nrow(filtered)



