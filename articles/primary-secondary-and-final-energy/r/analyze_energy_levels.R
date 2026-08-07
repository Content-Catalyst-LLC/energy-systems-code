args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- normalizePath(sub("^--file=", "", file_arg[1]))
root <- dirname(dirname(script_path))
input_path <- file.path(root, "data", "raw", "energy_pathways.csv")
output_path <- file.path(root, "outputs", "tables", "r_energy_levels.csv")

x <- read.csv(input_path, stringsAsFactors = FALSE)
transformation_input <- x$primary_energy_mwh * (1 - x$energy_sector_own_use_fraction - x$non_energy_use_fraction)
secondary <- transformation_input * x$conversion_efficiency
final <- secondary * x$delivery_efficiency
useful <- final * x$end_use_efficiency
service <- useful * x$service_factor
result <- data.frame(
  pathway = x$pathway,
  primary_energy_mwh = x$primary_energy_mwh,
  secondary_energy_mwh = secondary,
  final_energy_mwh = final,
  useful_energy_mwh = useful,
  service_energy_equivalent_mwh = service,
  residual_mwh = x$primary_energy_mwh - (
    x$primary_energy_mwh * x$energy_sector_own_use_fraction +
    x$primary_energy_mwh * x$non_energy_use_fraction +
    (transformation_input - secondary) +
    (secondary - final) +
    (final - useful) +
    (useful - service) + service
  )
)
write.csv(result, output_path, row.names = FALSE)
cat("Wrote", output_path, "\n")
