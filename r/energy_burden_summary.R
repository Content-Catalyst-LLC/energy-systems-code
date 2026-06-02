# Base R energy burden summary

args <- commandArgs(trailingOnly = FALSE)
file_arg <- "--file="
script_path <- sub(file_arg, "", grep(file_arg, args, value = TRUE))
if (length(script_path) > 0) {
  root <- normalizePath(file.path(dirname(script_path[1]), ".."), mustWork = FALSE)
} else {
  root <- getwd()
}

input <- file.path(root, "data", "synthetic", "household_energy_burden.csv")
output <- file.path(root, "outputs", "tables", "r_energy_burden_summary.csv")
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)

burden <- read.csv(input)
burden$energy_burden <- burden$annual_energy_cost_usd / burden$income_usd_yr
summary <- aggregate(energy_burden ~ region + housing_type, data = burden, FUN = mean)

write.csv(summary, output, row.names = FALSE)
cat("Wrote", output, "\n")
