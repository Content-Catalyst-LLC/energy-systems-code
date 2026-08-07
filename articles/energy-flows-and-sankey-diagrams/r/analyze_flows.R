args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
input <- file.path(root, "data", "processed", "energy_flows.csv")
output <- file.path(root, "outputs", "tables", "r_category_totals.csv")

x <- read.csv(input, stringsAsFactors = FALSE)
totals <- aggregate(value_mwh ~ category, data = x, FUN = sum)
write.csv(totals, output, row.names = FALSE)
cat("Wrote", output, "\n")
