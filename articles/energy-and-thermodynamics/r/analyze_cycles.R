args <- commandArgs(trailingOnly = TRUE)
article_dir <- if (length(args) >= 1) args[[1]] else "."
input_path <- file.path(article_dir, "data", "raw", "thermal_processes.csv")
output_path <- file.path(article_dir, "outputs", "tables", "r_cycle_metrics.csv")

processes <- read.csv(input_path, stringsAsFactors = FALSE)
processes$carnot_efficiency <- 1 - processes$cold_temperature_k / processes$hot_temperature_k
processes$actual_efficiency <- processes$carnot_efficiency * processes$second_law_fraction
processes$work_output_mj <- processes$heat_input_mj * processes$actual_efficiency
processes$heat_rejected_mj <- processes$heat_input_mj - processes$work_output_mj
processes$entropy_generation_mj_per_k <- (
  processes$heat_rejected_mj / processes$cold_temperature_k -
  processes$heat_input_mj / processes$hot_temperature_k
)
processes$first_law_residual_mj <- (
  processes$heat_input_mj - processes$work_output_mj - processes$heat_rejected_mj
)

result <- processes[, c(
  "scenario", "carnot_efficiency", "actual_efficiency", "work_output_mj",
  "heat_rejected_mj", "entropy_generation_mj_per_k", "first_law_residual_mj"
)]
write.csv(result, output_path, row.names = FALSE)
cat("Wrote", output_path, "\n")
