# Base R energy summary

args <- commandArgs(trailingOnly = FALSE)
file_arg <- "--file="
script_path <- sub(file_arg, "", grep(file_arg, args, value = TRUE))
if (length(script_path) > 0) {
  root <- normalizePath(file.path(dirname(script_path[1]), ".."), mustWork = FALSE)
} else {
  root <- getwd()
}

input <- file.path(root, "data", "synthetic", "hourly_load_and_renewables.csv")
output <- file.path(root, "outputs", "tables", "r_hourly_energy_summary.csv")
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)

energy <- read.csv(input)
energy$renewables_mwh <- energy$solar_mwh + energy$wind_mwh
summary <- data.frame(
  total_demand_mwh = sum(energy$demand_mwh),
  total_solar_mwh = sum(energy$solar_mwh),
  total_wind_mwh = sum(energy$wind_mwh),
  renewable_share_of_demand = sum(energy$renewables_mwh) / sum(energy$demand_mwh),
  peak_demand_mwh = max(energy$demand_mwh)
)

write.csv(summary, output, row.names = FALSE)
cat("Wrote", output, "\n")
