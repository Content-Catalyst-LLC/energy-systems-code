args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else getwd()
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = FALSE)
input <- file.path(root, "outputs", "tables", "scenario_summary.csv")
output <- file.path(root, "outputs", "tables", "r_scenario_metrics.csv")
if (!file.exists(input)) stop(paste("Missing input:", input))
x <- read.csv(input, check.names = FALSE)
x$useful_share <- x$useful_energy_kwh / x$energy_kwh
x$loss_share <- x$losses_kwh / x$energy_kwh
x$peak_to_mean_ratio <- x$peak_power_kw / x$mean_power_kw
write.csv(x, output, row.names = FALSE); cat("Wrote", output, "\n")
