# Simple Julia emissions intensity example

generation = [1000.0, 800.0, 600.0, 500.0]
emissions_factors = [0.0, 370.0, 950.0, 12.0]

total_generation = sum(generation)
total_emissions = sum(generation .* emissions_factors)
intensity = total_emissions / total_generation

mkpath(joinpath(@__DIR__, "..", "outputs", "tables"))
output = joinpath(@__DIR__, "..", "outputs", "tables", "julia_emissions_intensity.csv")
open(output, "w") do io
    println(io, "total_generation_mwh,total_emissions_kg,intensity_kg_mwh")
    println(io, "$(total_generation),$(total_emissions),$(round(intensity, digits=3))")
end

println("Wrote $output")
