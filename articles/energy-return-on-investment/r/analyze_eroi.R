args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
input <- file.path(root, "data", "processed", "eroi_projects.csv")
output <- file.path(root, "outputs", "tables", "r_eroi_summary.csv")

x <- read.csv(input, stringsAsFactors = FALSE)
invested_cols <- c(
  "construction_mwh",
  "fuel_cycle_mwh",
  "operations_mwh",
  "maintenance_mwh",
  "replacement_mwh",
  "network_mwh",
  "storage_mwh",
  "retirement_mwh"
)

x$invested_mwh <- rowSums(x[invested_cols])
x$eroi <- x$gross_output_mwh / x$invested_mwh
x$net_energy_mwh <- x$gross_output_mwh - x$invested_mwh

write.csv(
  x[c("name", "gross_output_mwh", "invested_mwh", "eroi", "net_energy_mwh")],
  output,
  row.names = FALSE
)
cat("Wrote", output, "\n")
