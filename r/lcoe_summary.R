# Base R LCOE assumption summary

args <- commandArgs(trailingOnly = FALSE)
file_arg <- "--file="
script_path <- sub(file_arg, "", grep(file_arg, args, value = TRUE))
if (length(script_path) > 0) {
  root <- normalizePath(file.path(dirname(script_path[1]), ".."), mustWork = FALSE)
} else {
  root <- getwd()
}

input <- file.path(root, "data", "synthetic", "lcoe_assumptions.csv")
output <- file.path(root, "outputs", "tables", "r_lcoe_input_summary.csv")
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)

lcoe <- read.csv(input)
summary <- data.frame(
  technology = lcoe$technology,
  capacity_factor = lcoe$capacity_factor,
  capex_usd_kw = lcoe$capex_usd_kw,
  fuel_usd_mwh = lcoe$fuel_usd_mwh
)

write.csv(summary, output, row.names = FALSE)
cat("Wrote", output, "\n")
