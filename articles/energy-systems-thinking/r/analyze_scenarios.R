args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
x <- read.csv(file.path(root,"outputs","tables","scenario_summary.csv"), stringsAsFactors=FALSE)
x <- x[order(-x$final_capacity_gw),]
write.csv(x,file.path(root,"outputs","tables","r_scenario_ranking.csv"),row.names=FALSE)
