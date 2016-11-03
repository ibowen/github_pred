# load repo weights table
edges <- read.csv(file.choose(), header=TRUE)
names(edges) <- c("source", "destination", "weight_by_follower", "weight_by_pub_repo", "weight_combined", "number_common_users")

edges$source <- as.character(edges$source)
edges$destination <- as.character(edges$destination)
edges$source <- tolower(edges$source)
edges$destination <- tolower(edges$destination)

# load repo features
nodes <- read.csv(file.choose(), header=TRUE)
nodes$full_name <- tolower(nodes$full_name)

map <- nodes[c("repo_id", "full_name")]
map$full_name <- as.character(map$full_name)
map$full_name <- tolower(map$full_name)

join1 <- merge(x = edges, y = map, by.x = "source", by.y = "full_name", all.x = TRUE)
names(join1) <- c("source", "destination", "weight_by_follower", "weight_by_pub_repo", "weight_combined", "number_common_users", "source_id")

join2 <- merge(x = join1, y = map, by.x = "destination", by.y = "full_name", all.x = TRUE)
names(join2) <- c("source", "destination", "weight_by_follower", "weight_by_pub_repo", "weight_combined", "number_common_users", "dest_id", "source_id")

edges_new <- join2[c("source_id","source","dest_id","destination","weight_by_follower", "weight_by_pub_repo", "weight_combined", "number_common_users")]
write.csv(edges_new, file="edges.csv",sep=",",row.names=FALSE,col.names=TRUE)
write.csv(nodes, file="nodes.csv", sep=",", row.names=FALSE, col.names=TRUE)