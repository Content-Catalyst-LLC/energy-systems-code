args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
root <- if (length(file_arg)) {
  normalizePath(file.path(dirname(sub("^--file=", "", file_arg[1])), ".."), mustWork = FALSE)
} else {
  normalizePath(".", mustWork = FALSE)
}

input <- file.path(root, "outputs", "tables", "scenario_summary.csv")
output <- file.path(root, "outputs", "tables", "r_system_metrics.csv")
scenarios <- read.csv(input, check.names = FALSE)

summary <- data.frame(
  scenario = scenarios$scenario,
  useful_service_mwh_equivalent = scenarios$useful_service_mwh_equivalent,
  efficiency_percent = 100 * scenarios$overall_primary_to_service_efficiency,
  renewable_share_percent = 100 * scenarios$renewable_input_share,
  emissions_t_co2e = scenarios$emissions_t_co2e,
  critical_service_percent = 100 * scenarios$critical_service_served_share
)

write.csv(summary, output, row.names = FALSE)
cat("Wrote", output, "\n")
