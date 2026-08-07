args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
input <- file.path(root, "outputs", "tables", "resilience_scenarios.csv")
output <- file.path(root, "outputs", "tables", "r_resilience_ranking.csv")

x <- read.csv(input, stringsAsFactors = FALSE)
x <- x[order(x$annualized_risk_million_usd), ]
write.csv(x, output, row.names = FALSE)
cat("Wrote", output, "\n")
