args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
input <- file.path(root, "outputs", "tables", "feeder_summary.csv")
output <- file.path(root, "outputs", "tables", "r_feeder_ranking.csv")

x <- read.csv(input, stringsAsFactors = FALSE)
x$utilization_percent <- 100 * x$utilization
x <- x[order(-x$utilization), ]
write.csv(x, output, row.names = FALSE)
cat("Wrote", output, "\n")
