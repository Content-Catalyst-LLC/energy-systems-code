.headers on
.mode csv
SELECT
  pathway,
  primary_energy_mwh,
  primary_energy_mwh * (1 - energy_sector_own_use_fraction - non_energy_use_fraction) * conversion_efficiency AS secondary_energy_mwh,
  primary_energy_mwh * (1 - energy_sector_own_use_fraction - non_energy_use_fraction) * conversion_efficiency * delivery_efficiency AS final_energy_mwh,
  primary_energy_mwh * (1 - energy_sector_own_use_fraction - non_energy_use_fraction) * conversion_efficiency * delivery_efficiency * end_use_efficiency AS useful_energy_mwh,
  primary_energy_mwh * (1 - energy_sector_own_use_fraction - non_energy_use_fraction) * conversion_efficiency * delivery_efficiency * end_use_efficiency * service_factor AS service_energy_equivalent_mwh
FROM energy_pathway
ORDER BY pathway;
