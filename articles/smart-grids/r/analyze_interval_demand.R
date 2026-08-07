args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
input <- file.path(root, "data", "raw", "interval_demand.csv")
output <- file.path(root, "outputs", "tables", "r_interval_analysis.csv")

x <- read.csv(input, stringsAsFactors = FALSE)
peak <- max(x$demand_mw)
x$above_75_mw <- x$demand_mw > 75
x$percent_of_peak <- 100 * x$demand_mw / peak
write.csv(x, output, row.names = FALSE)
cat("Wrote", output, "\n")
