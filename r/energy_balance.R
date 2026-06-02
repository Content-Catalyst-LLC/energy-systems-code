# Dependency-light R energy balance workflow.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- "--file="
script_arg <- args[grepl(file_arg, args)]

if (length(script_arg) > 0) {
  script_path <- normalizePath(sub(file_arg, "", script_arg[1]), mustWork = FALSE)
  root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = FALSE)
} else {
  root <- getwd()
}

input_path <- file.path(root, "data", "synthetic", "hourly_energy_profile.csv")
output_path <- file.path(root, "outputs", "tables", "r_energy_summary.csv")

if (!file.exists(input_path)) {
  stop(paste("Input file not found:", input_path))
}

df <- read.csv(input_path)
df$renewable_mwh <- df$solar_mwh + df$wind_mwh
df$renewable_share <- df$renewable_mwh / df$demand_mwh
df$thermal_gap_mwh <- pmax(0, df$demand_mwh - df$renewable_mwh)
df$thermal_used_proxy_mwh <- pmin(df$thermal_mwh, df$thermal_gap_mwh)
df$thermal_emissions_tco2 <- df$thermal_used_proxy_mwh * df$emissions_factor_tco2_per_mwh

summary <- data.frame(
  metric = c("total_demand_mwh", "total_renewable_mwh", "mean_renewable_share", "thermal_emissions_tco2"),
  value = c(
    sum(df$demand_mwh),
    sum(df$renewable_mwh),
    mean(df$renewable_share),
    sum(df$thermal_emissions_tco2)
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
write.csv(summary, output_path, row.names = FALSE)
print(summary)
cat("Output written to", output_path, "\n")
