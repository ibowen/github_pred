library(igraph)

dat <- read.csv(file.choose(), header=TRUE)
dat <- dat[which(dat$weight_by_follower != 0), ]

edges <- dat[c("source_id","dest_id","weight_by_follower")]
names(edges) <- c("from","to","weight")
edges$weight <- 1 / edges$weight

g <- graph.data.frame(edges,directed=FALSE) # this will create an 'igraph object'

# adjacency matrix
adj <- as_adjacency_matrix(g, attr="weight")
write.table(as.matrix(adj), file="matrix")

# network metrics
deg <- degree(g, mode="all")
deg.dist <- degree_distribution(g, cumulative=T, mode="all")
plot(x=0:max(deg), y=1-deg.dist, pch=19, cex=1.2, col="orange", 
      xlab="Degree", ylab="Cumulative Frequency")

bet <- betweenness(g, directed = FALSE)
close <- closeness(g)

degList <- as.data.frame(deg)
betweennessList <- as.data.frame(bet)
closenessList <- as.data.frame(close)






